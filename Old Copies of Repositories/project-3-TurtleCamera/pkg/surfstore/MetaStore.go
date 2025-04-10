// cmd/pkg/surfstore/MetaStore.go
package surfstore

import (
	context "context"
	emptypb "google.golang.org/protobuf/types/known/emptypb"
	"fmt"
)

type MetaStore struct {
	FileMetaMap    map[string]*FileMetaData
	BlockStoreAddr string
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

func (m *MetaStore) GetBlockStoreAddr(ctx context.Context, _ *emptypb.Empty) (*BlockStoreAddr, error) {
	// Extract the address of the block store from the MetaStore struct
	address := m.BlockStoreAddr

	// Create a new BlockStoreAddr message
	blockStoreAddr := &BlockStoreAddr{
		Addr: address,
	}

	// Return the BlockStoreAddr message and nil error
	return blockStoreAddr, nil
}

// This line guarantees all method for MetaStore are implemented
var _ MetaStoreInterface = new(MetaStore)

func NewMetaStore(blockStoreAddr string) *MetaStore {
	return &MetaStore{
		FileMetaMap:    map[string]*FileMetaData{},
		BlockStoreAddr: blockStoreAddr,
	}
}
