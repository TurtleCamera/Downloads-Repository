package surfstore

import (
	context "context"
	emptypb "google.golang.org/protobuf/types/known/emptypb"
	"fmt"
)

type MetaStore struct {
	FileMetaMap        map[string]*FileMetaData
	BlockStoreAddrs    []string
	ConsistentHashRing *ConsistentHashRing
	UnimplementedMetaStoreServer
}

func (m *MetaStore) GetFileInfoMap(ctx context.Context, _ *emptypb.Empty) (*FileInfoMap, error) {
	// Check if the FileMetaMap is initialized
	if m.FileMetaMap == nil {
		m.FileMetaMap = make(map[string]*FileMetaData)
	}

	// Wrap the FileMetaMap in a FileInfoMap message and return
	fileInfoMap := &FileInfoMap{
		FileInfoMap: m.FileMetaMap,
	}

	return fileInfoMap, nil
}

func (m *MetaStore) UpdateFile(ctx context.Context, fileMetaData *FileMetaData) (*Version, error) {
    // Check if the file exists in the map
	name := fileMetaData.Filename
	newVersion := fileMetaData.Version
    existingFileMeta, exists := m.FileMetaMap[name]

    // If the file doesn't exist, store the file and return the current newVersion
    if !exists {
        // Update the FileInfo values with the provided hash list
        existingFileMeta = fileMetaData

        // Update the FileInfoMap with the modified FileInfo
        m.FileMetaMap[name] = existingFileMeta

        return &Version{Version: newVersion}, nil
    }

    // Check if the new newVersion number is exactly one greater than the current newVersion number
	oldVersion := existingFileMeta.Version
    if newVersion != oldVersion + 1 {
        // If not, return an error with the current newVersion number
        return &Version{Version: -1}, fmt.Errorf("Invalid Version number. Expected Version %d", oldVersion + 1)
    }

    // Update the FileInfo values with the provided hash list
    existingFileMeta.BlockHashList = fileMetaData.BlockHashList
    existingFileMeta.Version = fileMetaData.Version

    // Update the FileInfoMap with the modified FileInfo
    m.FileMetaMap[name] = existingFileMeta

    // Return the updated newVersion number
    return &Version{Version: newVersion}, nil
}

// Given a list of block hashes, find out which block server they belong to
func (m *MetaStore) GetBlockStoreMap(ctx context.Context, blockHashesIn *BlockHashes) (*BlockStoreMap, error) {
	// Create a map to store the mapping of block store addresses to block hashes
	storeMap := make(map[string]*BlockHashes)

	// Iterate over the block store addresses
	for _, blockStoreAddr := range m.BlockStoreAddrs {
		storeMap[blockStoreAddr] = &BlockHashes{
			Hashes: make([]string, 0),
		}
	}

	// Iterate over the block hashes
	for _, hash := range blockHashesIn.Hashes {
		// Get the responsible server using consistent hashing
		responsibleServer := m.ConsistentHashRing.GetResponsibleServer(hash)

		// Add the block hash to the corresponding BlockHashes instance
		storeMap[responsibleServer].Hashes = append(storeMap[responsibleServer].Hashes, hash)
	}

	// Create a BlockStoreMap instance
	blockStoreMap := &BlockStoreMap{
		BlockStoreMap: storeMap,
	}

	return blockStoreMap, nil
}

func (m *MetaStore) GetBlockStoreAddrs(ctx context.Context, _ *emptypb.Empty) (*BlockStoreAddrs, error) {
	// Create a new BlockStoreAddrs instance. Variable m already contains the block store addresses.
	blockStoreAddrs := &BlockStoreAddrs{
		BlockStoreAddrs: m.BlockStoreAddrs,
	}
	
	return blockStoreAddrs, nil
}

// This line guarantees all method for MetaStore are implemented
var _ MetaStoreInterface = new(MetaStore)

func NewMetaStore(blockStoreAddrs []string) *MetaStore {
	return &MetaStore{
		FileMetaMap:        map[string]*FileMetaData{},
		BlockStoreAddrs:    blockStoreAddrs,
		ConsistentHashRing: NewConsistentHashRing(blockStoreAddrs),
	}
}
