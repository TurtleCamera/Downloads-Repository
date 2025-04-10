package main

import (
	"encoding/binary"
	"fmt"
	"log"
	"os"
	"sort"
)

// Record represents a single record with a key and value.
type Record struct {
	Key   [10]byte
	Value [90]byte
}

// RecordSlice represents a slice of records.
type RecordSlice []Record

// Len returns the length of the record slice.
func (rs RecordSlice) Len() int {
	return len(rs)
}

// Less reports whether the record with index i should sort before the record with index j.
func (rs RecordSlice) Less(i, j int) bool {
	// Compare the keys lexicographically
	return string(rs[i].Key[:]) < string(rs[j].Key[:])
}

// Swap swaps the records with indexes i and j.
func (rs RecordSlice) Swap(i, j int) {
	rs[i], rs[j] = rs[j], rs[i]
}

func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	if len(os.Args) != 3 {
		log.Fatalf("Usage: %v inputfile outputfile\n", os.Args[0])
	}

	inputFile := os.Args[1]
	outputFile := os.Args[2]

	// Open the input file for reading
	file, err := os.Open(inputFile)
	if err != nil {
		log.Fatalf("Error opening input file: %v", err)
	}
	defer file.Close()

	// Read records from the input file
	records, err := readRecords(file)
	if err != nil {
		log.Fatalf("Error reading records: %v", err)
	}

	// Sort the records based on keys
	sort.Sort(RecordSlice(records))

	// Write the sorted records to the output file
	err = writeRecords(outputFile, records)
	if err != nil {
		log.Fatalf("Error writing sorted records to output file: %v", err)
	}

	log.Printf("Sorted records written to %s\n", outputFile)
}

// readRecords reads records from the given file and returns a slice of records.
func readRecords(file *os.File) ([]Record, error) {
	var records []Record

	// Calculate the number of records in the file
	fileInfo, err := file.Stat()
	if err != nil {
		return nil, fmt.Errorf("error getting file info: %v", err)
	}
	numRecords := fileInfo.Size() / 100 // Each record is 100 bytes

	// Read each record from the file
	for i := 0; i < int(numRecords); i++ {
		var record Record

		// Read the key
		if err := binary.Read(file, binary.LittleEndian, &record.Key); err != nil {
			return nil, fmt.Errorf("error reading key for record %d: %v", i+1, err)
		}

		// Read the value
		if err := binary.Read(file, binary.LittleEndian, &record.Value); err != nil {
			return nil, fmt.Errorf("error reading value for record %d: %v", i+1, err)
		}

		records = append(records, record)
	}

	return records, nil
}

// writeRecords writes records to the given file.
func writeRecords(filename string, records []Record) error {
	// Open the output file for writing
	file, err := os.Create(filename)
	if err != nil {
		return fmt.Errorf("error creating output file: %v", err)
	}
	defer file.Close()

	// Write each record to the file
	for _, record := range records {
		// Write the key
		if err := binary.Write(file, binary.LittleEndian, record.Key); err != nil {
			return fmt.Errorf("error writing key to output file: %v", err)
		}

		// Write the value
		if err := binary.Write(file, binary.LittleEndian, record.Value); err != nil {
			return fmt.Errorf("error writing value to output file: %v", err)
		}
	}

	return nil
}
