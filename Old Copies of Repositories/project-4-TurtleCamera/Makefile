.PHONY: install
install:
	rm -rf bin
	GOBIN=$(PWD)/bin go install ./...

.PHONY: run-both
run-both:
	go run cmd/SurfstoreServerExec/main.go -d -s both -p 8081 -l localhost:8081

.PHONY: run-blockstore
run-blockstore:
	go run cmd/SurfstoreServerExec/main.go -s block -p 8081 -l

.PHONY: run-metastore
run-metastore:
	go run cmd/SurfstoreServerExec/main.go -s meta -l localhost:8081

.PHONY: run-multiple
run-multiple:
	go run cmd/SurfstoreServerExec/main.go -s block -p 8081 -l
	go run cmd/SurfstoreServerExec/main.go -s block -p 8082 -l
	go run cmd/SurfstoreServerExec/main.go -s meta -l localhost:8081 localhost:8082