package main

import "gRPC/KVStore"

func main() {
	// Step 1: Create a New Client KVStore
	rpcClient := KVStore.NewClient("localhost:8000")

	// Step 2: Make RPC Call
	rpcClient.Put("Balance", 200)
	rpcClient.Get("Balance")
}
