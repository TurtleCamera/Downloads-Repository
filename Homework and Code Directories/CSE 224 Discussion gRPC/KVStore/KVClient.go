package KVStore

import (
	"context"
	"fmt"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type Client struct {
	Addr string
}

func (client *Client) Put(key string, val int) error {
	// connect to the server
	conn, err := grpc.Dial(client.Addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return err
	}
	// Here this function comes from generate code from proto
	c := NewKVStoreClient(conn)

	// perform the call
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	success, err := c.Put(ctx, &KVPair{Key: key, Val: int32(val)})
	if err != nil {
		conn.Close()
		return err
	}
	fmt.Printf("Success : %v \n", success.GetFlag())

	// close the connection
	return conn.Close()
}

func (client *Client) Get(key string) error {
	// connect to the server
	conn, err := grpc.Dial(client.Addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return err
	}
	// Here this method comes from generate code by proto
	c := NewKVStoreClient(conn)

	// perform the call
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	val, err := c.Get(ctx, &Key{Key: key})

	fmt.Printf("Key: %v, Val: %v \n", key, val.Val)

	if err != nil {
		conn.Close()
		return err
	}

	// close the connection
	return conn.Close()
}

// Create an Surfstore RPC client
func NewClient(Addr string) Client {
	return Client{
		Addr: Addr,
	}
}
