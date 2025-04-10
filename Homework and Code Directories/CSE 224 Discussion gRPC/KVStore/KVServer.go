package KVStore

import (
	context "context"
	"fmt"
)

type InfoMap struct {
	Map map[string]int
}

func (infoMap *InfoMap) Get(ctx context.Context, key *Key) (*Value, error) {
	val, ok := infoMap.Map[key.Key]

	if !ok {
		return &Value{Val: -1}, fmt.Errorf("Key %v is not found in the map", key.Key)
	} else {
		return &Value{Val: int32(val)}, nil
	}
}

func (infoMap *InfoMap) Put(ctx context.Context, kvPair *KVPair) (*Success, error) {

	infoMap.Map[kvPair.Key] = int(kvPair.Val)
	return &Success{Flag: true}, nil
}

func NewInfoMap() *InfoMap {
	return &InfoMap{
		Map: make(map[string]int),
	}
}
