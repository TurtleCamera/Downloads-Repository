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
	// Connect to the server
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
	// Connect to the server
    conn, err := grpc.Dial(blockStoreAddr, grpc.WithInsecure())
    if err != nil {
        return err
    }
    defer conn.Close()

	// Create a client for the BlockStore service
    client := NewBlockStoreClient(conn)

	// Call the PutBlock RPC method
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
	// Connect to the server
	conn, err := grpc.Dial(blockStoreAddr, grpc.WithInsecure())
	if err != nil {
		return err
	}
	defer conn.Close()

	// Create a client for the BlockStore service
	blockClient := NewBlockStoreClient(conn)

	// Call the MissingBlocks RPC method
	blockHashes := &BlockHashes{Hashes: blockHashesIn}
    ctx := context.Background()
	response, err := blockClient.MissingBlocks(ctx, blockHashes)
	if err != nil {
		return err
	}

	// Update the blockHashesOut parameter with the missing block hashes received from the server
	*blockHashesOut = response.Hashes

	return nil
}

func (surfClient *RPCClient) GetBlockHashes(blockStoreAddr string, blockHashes *[]string) error {
    // Connect to the server
	conn, err := grpc.Dial(blockStoreAddr, grpc.WithInsecure())
    if err != nil {
        return err
    }
    defer conn.Close()

	// Create a client for the BlockStore service
    client := NewBlockStoreClient(conn)

    // Call the GetBlockHashes RPC method
    emptyMessage := &emptypb.Empty{}
    ctx := context.Background()
    response, err := client.GetBlockHashes(ctx, emptyMessage)
    if err != nil {
        return err
    }

    // Update blockHashes with the received block hashes
    *blockHashes = response.Hashes

    return nil
}

func (surfClient *RPCClient) GetFileInfoMap(serverFileInfoMap *map[string]*FileMetaData) error {
    // Connect to the server
    conn, err := grpc.Dial(surfClient.MetaStoreAddr, grpc.WithInsecure())
    if err != nil {
        return err
    }
    defer conn.Close()

    // Create a MetaStore client
    client := NewMetaStoreClient(conn)

    // Call the GetFileInfoMap RPC method to fetch the file information map
    ctx := context.Background()
    emptyMessage := &emptypb.Empty{}
    fileInfoMap, err := client.GetFileInfoMap(ctx, emptyMessage)
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

    // Call the UpdateFile RPC method and update the version
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

func (surfClient *RPCClient) GetBlockStoreMap(blockHashesIn []string, blockStoreMap *map[string][]string) error {
	// Connect to the server
    conn, err := grpc.Dial(surfClient.MetaStoreAddr, grpc.WithInsecure())
    if err != nil {
        return err
    }
    defer conn.Close()

    // Create a MetaStore client
    client := NewMetaStoreClient(conn)

    // Call the GetBlockStoreMap RPC method
    ctx := context.Background()
    blockHashes := &BlockHashes{Hashes: blockHashesIn}
    response, err := client.GetBlockStoreMap(ctx, blockHashes)
    if err != nil {
        return err
    }

    // Note: client.GetBlockStoreMap returns a BlockStoreMap, so we need to
    // convert the content to map[string][]string
    convertedMap := make(map[string][]string)
    responseMap := response.BlockStoreMap
    for address, blockHashes := range responseMap {
        convertedMap[address] = blockHashes.Hashes
    }

    // Update blockStoreMap with the converted map
    *blockStoreMap = convertedMap

    return nil
}

func (surfClient *RPCClient) GetBlockStoreAddrs(blockStoreAddrs *[]string) error {
	// Connect to the server
    conn, err := grpc.Dial(surfClient.MetaStoreAddr, grpc.WithInsecure())
    if err != nil {
        return err
    }
    defer conn.Close()

    // Create a MetaStore client
    metaClient := NewMetaStoreClient(conn)

    // Call the GetBlockStoreAddrs RPC method
    ctx := context.Background()
    emptyMessage := &emptypb.Empty{}
    response, err := metaClient.GetBlockStoreAddrs(ctx, emptyMessage)
    if err != nil {
        return err
    }

    // Update blockStoreAddrs with the received block store addresses
    *blockStoreAddrs = response.BlockStoreAddrs

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
