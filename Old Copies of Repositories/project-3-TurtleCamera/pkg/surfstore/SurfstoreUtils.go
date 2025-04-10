// cmetaData/pkg/surfstore/SurfstoreUtils.go

package surfstore

import (
	"io/ioutil"
	"os"
	"math"
	"io"
	"path/filepath"
	"fmt"
)

// Helper function for computing the hash value for a file's set of blocks
func calculateFileHashes(filePath string, blockSize float64) []string {
	file, fileErr := os.Open(filePath)
	if fileErr != nil {
		// log.Println("Error opening file:", fileErr)
		return nil
	}
	defer file.Close()

	stat, statErr := file.Stat()
	if statErr != nil {
		// log.Println("Error getting file stats:", statErr)
		return nil
	}

	totalFileSize := float64(stat.Size())
	numBlocks := int(math.Ceil(totalFileSize / blockSize))
	hashes := make([]string, 0, numBlocks)

	// The hash depends on whether or not the file is empty
	if totalFileSize <= 0 {
		// Set to -1 if the file size is 0
		fileHash := "-1"	
		hashes = append(hashes, fileHash)
	} else {
		// Create hashes for each block
		count := 0
		for count < numBlocks {
			slice := make([]byte, int(blockSize))
			n, err := file.Read(slice)
			if err != nil {
				if err != io.EOF {
					// log.Println("Error reading bytes from file:", err)
					return hashes
				}
			}

			// Create the hashes
			fileHash := GetBlockHashString(slice[:n])
			hashes = append(hashes, fileHash)

			count += 1
		}
	}

	return hashes
}

// Helper function to create a hash map
func generateHashMap(baseDir string, files []os.FileInfo, blockSize float64) map[string][]string {
	fileHashMap := make(map[string][]string)

	// Iterate through all files
	for _, file := range files {
		name := file.Name()

		// Ignore index.db because that's our database
		if name == "index.db" {
			continue
		}

		// Calculate the hash of the block of each file
		filePath := filepath.Join(baseDir, name)
		hashes := calculateFileHashes(filePath, blockSize)
		fileHashMap[name] = hashes
	}
	return fileHashMap
}

// Checks if hashes are equal
func isEqualBlockHashList(hashes1, hashes2 []string) bool {
	if len(hashes1) != len(hashes2) {
		return false
	}

	for i, hash := range hashes1 {
		if hash != hashes2[i] {
			return false
		}
	}

	return true
}

// Checks if the hash isn't a "0" (determine if we should turn into tombstone record)
func isTombstone(data *FileMetaData) bool {
	hashList := data.BlockHashList
    blockHashLength := len(hashList)
    firstCharacter := ""
    if blockHashLength > 0 {
        firstCharacter = hashList[0]
    }

    return firstCharacter == "0" && blockHashLength == 1
}

// Adds a new file to the meta data
func addNewMetadata(metaIndices map[string]*FileMetaData, fileName string, blockHashList []string) {
    meta := FileMetaData{
        Filename:       fileName,
        Version:        1,
        BlockHashList:  blockHashList,
    }
    metaIndices[fileName] = &meta
}

// Updates the meta data of the file
func (metaData *FileMetaData) update(hashList []string) {
	metaData.Version++
	metaData.BlockHashList = hashList
}

// This deletes the hash entry (tombstone record)
func (metaData *FileMetaData) invalidate() {
	metaData.Version++
	metaData.BlockHashList = []string{"0"}
}

func updateLocalIndex(metaIndices map[string]*FileMetaData, hashMap map[string][]string, fileInfoList []os.FileInfo) {
	// Unlike in Python, looping through the entries in metaIndices do
	// access references of the key and value inside of metaIndices, so
	// calling functions on them will modify them in metaIndices
	for _, file := range fileInfoList {
		name := file.Name()
		data, exists := metaIndices[name]
		hashes, _ := hashMap[name]

		// Ignore index.db because that's our database
		if name == "index.db" {
			continue
		}

		// If this file doesn't exist in the meta data, make a new entry
		if !exists {
			addNewMetadata(metaIndices, name, hashes)
			continue
		}
		
		// If the hashes are different, then update the data and metadata
		if !isEqualBlockHashList(hashes, data.BlockHashList) {
			data.update(hashes)
		}
	}

	// Next, check if we need to change anything for the tombstone records
	for name, data := range metaIndices {
		_, exists := hashMap[name]
		// Does this file no longer exist and the record isn't?
		if !exists && !isTombstone(data) {
			data.invalidate()
		}
	}
}

func getRemoteIndex(client RPCClient) map[string]*FileMetaData {
	// Create a map to retrieve the remote index
	remoteIndices := make(map[string]*FileMetaData)
	err := client.GetFileInfoMap(&remoteIndices)
	if err != nil {
		// log.Println("Error retrieving remote index:", err)
		return nil
	}
	return remoteIndices
}

// Downloads files to the client
func downloadFile(client RPCClient, remoteMetaData *FileMetaData, blockAddress string) error {
	baseDirectory := client.BaseDir
	name := remoteMetaData.Filename
    path := filepath.Join(baseDirectory, name)
	file, err := os.Create(path)
	if err != nil {
		return fmt.Errorf("Error creating the file: %v", err)
	}
	defer file.Close()
	
	// Check if the file was deleted (tombstone file)
	if isTombstone(remoteMetaData) {
		err := os.Remove(path)
		if err != nil {
			return fmt.Errorf("Error removing local file:", err)
		}
		return nil
	}

	// If we're here, then write all the blocks to the client
	hashList := remoteMetaData.BlockHashList
	for _, hash := range hashList {
		// Get the block
		var block Block
		err := client.GetBlock(hash, blockAddress, &block)
		if err != nil {
			return fmt.Errorf("Error when getting block:", err)
		}
	
		// Write this block to the client
		_, err = file.Write(block.BlockData)
		if err != nil {
			return fmt.Errorf("Failed to write block data to file:", err)
		}
	}

	return nil
}

// Uploads files to the server
func uploadFile(client RPCClient, metaData *FileMetaData, blockAddress string) error {
	baseDirectory := client.BaseDir
	name := metaData.Filename
	path := filepath.Join(baseDirectory, name)

	// Before doing anything, check if this file even exists
	_, existErr := os.Stat(path)
	if os.IsNotExist(existErr) {
		// If it doesn't exist, update the meta data. UpdateFile doesn't manually
		// update the version, so we will have to update it here.
		var newVersion int32
		err := client.UpdateFile(metaData, &newVersion)
		if err != nil {
			return fmt.Errorf("Error updating file: %v", err)
		}

		// Update the version
		metaData.Version = newVersion

		return fmt.Errorf("Error with non-existent file: %v", existErr)
	}

	// Read in the file
    file, err := os.Open(path)
    if err != nil {
        return fmt.Errorf("Error opening file: %v", err)
    }
    defer file.Close()

	// Upload all the blocks to the server
    fileStat, _ := file.Stat()
	fileSize := float64(fileStat.Size())
	blockSize := float64(client.BlockSize)
    numBlocks := int(math.Ceil(fileSize / blockSize))
	
    count := 0
    for count < numBlocks {
		// Read in the slice
        blockSize := client.BlockSize
        slice := make([]byte, blockSize)
        n, err := file.Read(slice)
        if err != nil {
            if err != io.EOF {
                return fmt.Errorf("Error reading bytes from file:", err)
            }
        }
    
		// Create a block and store it
        block := Block{
			BlockData: slice[:n],
			BlockSize: int32(n),
		}
        var succ bool
		err = client.PutBlock(&block, blockAddress, &succ)
        if err != nil {
            return fmt.Errorf("Error when putting block:", err)
        }
    
        count += 1
    }

	// Update the version of the file
    var newVersion int32
	err = client.UpdateFile(metaData, &newVersion);
    if err != nil {
		// An error means we should set the version to -1
        metaData.Version = -1
        return fmt.Errorf("Error when updating file:", err)
    }

	// Otherwise, update the meta data accordingly
	metaData.Version = newVersion

    return nil
}

// Logic for checking if files need to be downloaded to the client
func shouldDownload(exists bool, localMetaData, remoteMetaData *FileMetaData) bool {
	// There are three cases to download, with these priorities:
	// 1) The file doesn't exist on the client
	// 2) The server file has a higher version than the one on the client
	// 3) The versions are the same, but the hashes aren't
	return !exists ||
		localMetaData.Version < remoteMetaData.Version ||
		(localMetaData.Version == remoteMetaData.Version && !isEqualBlockHashList(localMetaData.BlockHashList, remoteMetaData.BlockHashList))
}

// Handles downloading of files from server to client
func handleDownload(client RPCClient, metaIndices, remoteIndices map[string]*FileMetaData, blockAddress string) {
	for name, remoteMetaData := range remoteIndices {
		localMetaData, exists := metaIndices[name]

		// Check if file needs to be downloaded
		if shouldDownload(exists, localMetaData, remoteMetaData) {
			metaIndices[name] = remoteMetaData // Update client meta data

			err := downloadFile(client, remoteMetaData, blockAddress)
			if err != nil {
				// log.Println("Error downloading file:", err)
				continue
			}
		}
	}
}

// Logic for checking if files need to be uploaded to the server
func shouldUpload(exists bool, localMetaData, remoteMetaData *FileMetaData) bool {
	// There are two cases to upload, with these priorities:
	// 1) The file doesn't exist in the server
	// 2) The client file has a higher version than the one on the server
	return !exists || localMetaData.Version > remoteMetaData.Version
}

// Handles uploading of files from client to server
func handleUpload(client RPCClient, metaIndices, remoteIndices map[string]*FileMetaData, blockAddress string) {
	for name, localMetaData := range metaIndices {
		remoteMetaData, exists := remoteIndices[name]

		// Check if file needs to be uploaded
		if shouldUpload(exists, localMetaData, remoteMetaData) {
			err := uploadFile(client, localMetaData, blockAddress)
			if err != nil {
				// log.Println("Error uploading file:", err)
				continue
			}
		}
	}
}

// Synchronizes the client and server
func uploadAndDownload(client RPCClient, metaIndices, remoteIndices map[string]*FileMetaData, blockAddress string) {
	// Handle downloading of files from server to client
	handleDownload(client, metaIndices, remoteIndices, blockAddress)
	
	// Handle uploading of files from client to server
	handleUpload(client, metaIndices, remoteIndices, blockAddress)
}

// ClientSync synchronizes the client's local files with the server.
func ClientSync(client RPCClient) {
	// Load the meta file
	baseDirectory := client.BaseDir
	metaIndices, err := LoadMetaFromMetaFile(baseDirectory)
	if err != nil {
		// log.Println("Error loading data from meta file:", err)
		return
	}

	// Read the files from the base directory
	files, err := ioutil.ReadDir(baseDirectory)
	if err != nil {
		// log.Println("Error loading files in base directory:", err)
		return
	}

	// Create a hash map where the keys are filenames and the values are
	// arrays of hash values corresponding to each block of the file
	blockSize := float64(client.BlockSize)
	fileHashMap := generateHashMap(baseDirectory, files, blockSize)

	// Update the meta data index based on the hash map
	updateLocalIndex(metaIndices, fileHashMap, files)

	// Get the block store address
	blockAddress := ""
	blockErr := client.GetBlockStoreAddr(&blockAddress)
	if blockErr != nil {
		// log.Println("Error getting block store address:", blockErr)
		return
	}

	// Use the RPC client to retrieve the remote index of files
	remoteIndices := getRemoteIndex(client)

	// Synchronize the server and client
	uploadAndDownload(client, metaIndices, remoteIndices, blockAddress)

	// Finally, write the meta file
	WriteMetaFile(metaIndices, baseDirectory)
}