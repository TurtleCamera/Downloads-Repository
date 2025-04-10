package surfstore

import (
	"crypto/sha256"
	"encoding/hex"
	"sort"
)

type ConsistentHashRing struct {
	ServerMap map[string]string
}

func (c ConsistentHashRing) GetResponsibleServer(blockHash string) string {
	// The keys of c.ServerMap contain the hashes for the server addresses.
	// Retrieve them from the consistent hash ring and sort them
	hashes := make([]string, 0, len(c.ServerMap))
	for hash := range c.ServerMap {
		hashes = append(hashes, hash)
	}
	sort.Strings(hashes)

	// Find the first server with hash value that's larger than the block hash
	responsibleServer := ""
	for _, hash := range hashes {
		if hash > blockHash {
			responsibleServer = c.ServerMap[hash]
			break
		}
	}

	// Wrap around to the first server if no server has a larger
	// hash value than the block hash
	if responsibleServer == "" {
		firstServerHash := hashes[0]
		responsibleServer = c.ServerMap[firstServerHash]
	}

	return responsibleServer
}

func (c ConsistentHashRing) Hash(addr string) string {
	h := sha256.New()
	h.Write([]byte(addr))
	return hex.EncodeToString(h.Sum(nil))

}

func NewConsistentHashRing(serverAddrs []string) *ConsistentHashRing {
	// Initialize the ConsistentHashRing
	serverMap := make(map[string]string)
	hashRing := &ConsistentHashRing{
		ServerMap: serverMap,
	}

	// Populate ServerMap with hashed addresses
	for _, address := range serverAddrs {
		// Each block server will have a name in the format of "blockstore" + address
		addressWithPrefix := "blockstore" + address
		hashedAddr := hashRing.Hash(addressWithPrefix)
		
		hashRing.ServerMap[hashedAddr] = address
	}

	return hashRing
}