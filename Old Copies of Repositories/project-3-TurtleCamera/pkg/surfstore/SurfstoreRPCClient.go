// cmd/pkg/surfstore/SurfstoreRPCClient.go

package surfstore

import (
	context "context"
    "google.golang.org/protobuf/types/known/emptypb"
	"time"

	grpc "google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type RPCClient struct {
	MetaStoreAddr string
	BaseDir       string
	BlockSize     int
}

func (surfClient *RPCClient) GetBlock(blockHash string, blockStoreAddr string, block *Block) error {
	// connect to the server
	conn, err := grpc.Dial(blockStoreAddr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return err
	}
	c := NewBlockStoreClient(conn)

	// perform the call
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	b, err := c.GetBlock(ctx, &BlockHash{Hash: blockHash})
	if err != nil {
		conn.Close()
		return err
	}
	block.BlockData = b.BlockData
	block.BlockSize = b.BlockSize

	// close the connection
	return conn.Close()
}

func (surfClient *RPCClient) PutBlock(block *Block, blockStoreAddr string, succ *bool) error {
    // Dial the gRPC server
    conn, err := grpc.Dial(blockStoreAddr, grpc.WithInsecure())
    if err != nil {
        return err
    }
    defer conn.Close()

    // Create a client stub for the BlockStore service
    client := NewBlockStoreClient(conn)

    // Call the PutBlock RPC method on the server using the client stub
    ctx := context.Background()
    response, err := client.PutBlock(ctx, block)
    if err != nil {
        return err
    }

    // Update the success flag
    *succ = response.Flag

    return nil
}

func (surfClient *RPCClient) MissingBlocks(blockHashesIn []string, blockStoreAddr string, blockHashesOut *[]string) error {
	// Dial the connection to the BlockStore server
	conn, err := grpc.Dial(blockStoreAddr, grpc.WithInsecure())
	if err != nil {
		return err
	}
	defer conn.Close()

	// Create a client for the BlockStore service
	blockClient := NewBlockStoreClient(conn)

	// Call the MissingBlocks RPC method
    ctx := context.Background()
	blockHashes := &BlockHashes{Hashes: blockHashesIn}
	response, err := blockClient.MissingBlocks(ctx, blockHashes)
	if err != nil {
		return err
	}

	// Update the blockHashesOut parameter with the missing block hashes received from the server
	*blockHashesOut = response.Hashes

	return nil
}

func (surfClient *RPCClient) GetFileInfoMap(serverFileInfoMap *map[string]*FileMetaData) error {
    // Connect to the server
    conn, err := grpc.Dial(surfClient.MetaStoreAddr, grpc.WithInsecure())
    if err != nil {
        return err
    }
    defer conn.Close()

    // Create a client instance for the MetaStore service
    client := NewMetaStoreClient(conn)

    // Make a remote procedure call (RPC) to fetch the file information map
    ctx := context.Background()
    emptyMsg := &emptypb.Empty{}
    fileInfoMap, err := client.GetFileInfoMap(ctx, emptyMsg)
    if err != nil {
        return err
    }

    // Populate the provided map pointer with the received file information map
    *serverFileInfoMap = fileInfoMap.FileInfoMap

    return nil
}

func (surfClient *RPCClient) UpdateFile(fileMetaData *FileMetaData, latestVersion *int32) error {
    // Connect to the server
    conn, err := grpc.Dial(surfClient.MetaStoreAddr, grpc.WithInsecure())
    if err != nil {
        return err
    }
    defer conn.Close()

    // Create a MetaStore client
    client := NewMetaStoreClient(conn)

    // Perform the call and update the version
    ctx := context.Background()
    version, err := client.UpdateFile(ctx, fileMetaData)
    newVersion := version.Version
    if err != nil {
        return err
    }

    // Fixed issue: The logic for updating the version is in client.UpdateFile and it
    // will return the version we're supposed to set *latestVersion to.
    *latestVersion = newVersion

    return nil
}

func (surfClient *RPCClient) GetBlockStoreAddr(blockStoreAddr *string) error {
    // Connect to the server
    conn, err := grpc.Dial(surfClient.MetaStoreAddr, grpc.WithInsecure())
    if err != nil {
        return err
    }
    defer conn.Close()

    // Create a MetaStore client
    client := NewMetaStoreClient(conn)

    // Perform the call
    ctx := context.Background()

    response, err := client.GetBlockStoreAddr(ctx, &emptypb.Empty{})
    if err != nil {
        return err
    }

    // Populate the blockStoreAddr pointer with the received address
    *blockStoreAddr = response.Addr

    return nil
}

// This line guarantees all method for RPCClient are implemented
var _ ClientInterface = new(RPCClient)

// Create an Surfstore RPC client
func NewSurfstoreRPCClient(hostPort, baseDir string, blockSize int) RPCClient {

	return RPCClient{
		MetaStoreAddr: hostPort,
		BaseDir:       baseDir,
		BlockSize:     blockSize,
	}
}
