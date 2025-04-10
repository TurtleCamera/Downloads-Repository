func (s *RaftSurfstore) MakeServerUnreachableFrom(ctx context.Context, servers *UnreachableFromServers) (*Success, error) {
	s.raftStateMutex.Lock()
	if len(servers.ServerIds) == 0 {
		s.unreachableFrom = make(map[int64]bool)
		log.Printf("Server %d is reachable from all servers", s.id)
	} else {
		for _, serverId := range servers.ServerIds {
			s.unreachableFrom[serverId] = true
		}
		log.Printf("Server %d is unreachable from %v", s.id, s.unreachableFrom)
	}

	s.raftStateMutex.Unlock()

	return &Success{Flag: true}, nil
}

func TestRaftNetworkPartitionWithConcurrentRequests(t *testing.T) {
	t.Log("leader1 gets 1 request while the majority of the cluster is unreachable. As a result of a (one way) network partition, leader1 ends up with the minority. leader2 from the majority is elected")
	// 	// A B C D E
	cfgPath := "./config_files/5nodes.txt"
	test := InitTest(cfgPath)
	defer EndTest(test)

	filemeta1 := &surfstore.FileMetaData{
		Filename:      "testFile1",
		Version:       1,
		BlockHashList: nil,
	}
	filemeta2 := &surfstore.FileMetaData{
		Filename:      "testFile2",
		Version:       1,
		BlockHashList: nil,
	}

	A := 0
	C := 2
	// D := 3
	E := 4

	// A is leader
	leaderIdx := A
	test.Clients[leaderIdx].SetLeader(test.Context, &emptypb.Empty{})
	test.Clients[leaderIdx].SendHeartbeat(test.Context, &emptypb.Empty{})

	// Partition happens
	// C D E are unreachable
	unreachableFromServers := &surfstore.UnreachableFromServers{
		ServerIds: []int64{0, 1},
	}
	for i := C; i <= E; i++ {
		test.Clients[i].MakeServerUnreachableFrom(test.Context, unreachableFromServers)
	}

	blockChan := make(chan bool)

	// A gets an entry and pushes to A and B
	go func() {
		// This should block though and fail to commit when getting the RPC response from the new leader
		_, _ = test.Clients[leaderIdx].UpdateFile(test.Context, filemeta1)
		blockChan <- false
	}()

	go func() {
		<-time.NewTimer(5 * time.Second).C
		blockChan <- true
	}()

	if !(<-blockChan) {
		t.Fatalf("Request did not block")
	}

	// C becomes leader
	leaderIdx = C
	test.Clients[leaderIdx].SetLeader(test.Context, &emptypb.Empty{})
	test.Clients[leaderIdx].SendHeartbeat(test.Context, &emptypb.Empty{})
	// C D E are restored
	for i := C; i <= E; i++ {
		test.Clients[i].MakeServerUnreachableFrom(test.Context, &surfstore.UnreachableFromServers{ServerIds: []int64{}})
	}

	test.Clients[leaderIdx].SendHeartbeat(test.Context, &emptypb.Empty{})
	time.Sleep(time.Second)

	// Every node should have an empty log
	goldenLog := make([]*surfstore.UpdateOperation, 0)
	goldenLog = append(goldenLog, &surfstore.UpdateOperation{
		Term:         1,
		FileMetaData: nil,
	})
	goldenLog = append(goldenLog, &surfstore.UpdateOperation{
		Term:         2,
		FileMetaData: nil,
	})
	// Leaders should not commit entries that were created in previous terms.
	goldenMeta := make(map[string]*surfstore.FileMetaData)
	term := int64(2)

	for idx, server := range test.Clients {

		_, err := CheckInternalState(nil, &term, goldenLog, goldenMeta, server, test.Context)
		if err != nil {
			t.Fatalf("Error checking state for server %d: %s", idx, err.Error())
		}
	}

	go func() {
		test.Clients[leaderIdx].UpdateFile(test.Context, filemeta1)
		test.Clients[leaderIdx].SendHeartbeat(test.Context, &emptypb.Empty{})
	}()
	go func() {
		test.Clients[leaderIdx].UpdateFile(test.Context, filemeta2)
		test.Clients[leaderIdx].SendHeartbeat(test.Context, &emptypb.Empty{})
	}()

	//Enough time for things to settle
	time.Sleep(2 * time.Second)
	test.Clients[leaderIdx].SendHeartbeat(test.Context, &emptypb.Empty{})

	goldenMeta[filemeta1.Filename] = filemeta1
	goldenMeta[filemeta2.Filename] = filemeta2

	goldenLog = append(goldenLog, &surfstore.UpdateOperation{
		Term:         2,
		FileMetaData: filemeta1,
	})
	goldenLog = append(goldenLog, &surfstore.UpdateOperation{
		Term:         2,
		FileMetaData: filemeta2,
	})

	for idx, server := range test.Clients {

		state, err := server.GetInternalState(test.Context, &emptypb.Empty{})
		if err != nil {
			t.Fatalf("could not get internal state: %s", err.Error())
		}
		if state == nil {
			t.Fatalf("state is nil")
		}

		if len(state.Log) != 4 {
			t.Fatalf("Should have 4 logs")
		}

		if err != nil {
			t.Fatalf("Error checking state for server %d: %s", idx, err.Error())
		}
	}
}
