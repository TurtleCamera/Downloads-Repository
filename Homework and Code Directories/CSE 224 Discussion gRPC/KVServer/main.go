package main

import (
	"gRPC/KVStore"
	"google.golang.org/grpc"
	"log"
	"net"
)

func main() {
	log.Fatal(startServer("localhost:8000"))
}

func startServer(hostAddr string) error {

	//Step 1 : Create a new Server
	grpcServer := grpc.NewServer()

	//Step 2: Register rpc services
	srv := KVStore.NewInfoMap()
	KVStore.RegisterKVStoreServer(grpcServer, srv)

	//Step 3: start listening on hostAddr
	l, e := net.Listen("tcp", hostAddr)
	if e != nil {
		return e
	}
	return grpcServer.Serve(l)
}
