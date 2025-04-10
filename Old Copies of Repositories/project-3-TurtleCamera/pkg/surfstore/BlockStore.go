// cmd/pkg/surfstore/BlockStore.go
package surfstore

import (
	context "context"
	"fmt"
	"crypto/sha256"
	"encoding/hex"
)

type BlockStore struct {
	BlockMap map[string]*Block
	UnimplementedBlockStoreServer
}

func (bs *BlockStore) GetBlock(ctx context.Context, blockHash *BlockHash) (*Block, error) {
	// Check if the block hash exists in the block store
	block, found := bs.BlockMap[blockHash.Hash]
	if !found {
		return nil, fmt.Errorf("Error finding block for hash: %s", blockHash.Hash)
	}

	return block, nil
}

func (bs *BlockStore) PutBlock(ctx context.Context, block *Block) (*Success, error) {
	// Calculate the hash of the block's data.
	hash := sha256.New()
	hash.Write(block.BlockData)
	hashBytes := hash.Sum(nil)

	// Convert the hash bytes to a hexadecimal string.
	hashString := hex.EncodeToString(hashBytes)

	// Create a new Block instance with the block's data and size.
	newBlock := &Block{
		BlockData: block.BlockData,
		BlockSize: block.BlockSize,
	}

	// Store the block in the block map using the hash string as the key.
	bs.BlockMap[hashString] = newBlock

	// Set the success status to true.
	success := &Success{
		Flag: true,
	}

	return success, nil
}	

// Given a list of hashes “in”, returns a list containing the
// hashes that are not stored in the key-value store
func (bs *BlockStore) MissingBlocks(ctx context.Context, blockHashesIn *BlockHashes) (*BlockHashes, error) {
	missingBlockHashes := &BlockHashes{}

	// Iterate over the input list of block hashes
	for _, hash := range blockHashesIn.Hashes {
		// Check if the block hash exists in the BlockMap
		_, exists := bs.BlockMap[hash]
		if !exists {
			// If the block hash does not exist, append it to the list of missing block hashes
			missingBlockHashes.Hashes = append(missingBlockHashes.Hashes, hash)
		}
	}

	// Return the list of missing block hashes
	return missingBlockHashes, nil
}

// This line guarantees all method for BlockStore are implemented
var _ BlockStoreInterface = new(BlockStore)

func NewBlockStore() *BlockStore {
	return &BlockStore{
		BlockMap: map[string]*Block{},
	}
}
