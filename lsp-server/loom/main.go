package main

import (
	"bufio"
	"encoding/json"
	"io"
	"log"
	"loom/analysis"
	"loom/lsp"
	"loom/rpc"
	"os"

	"time"
)

func main() {
	logger := getLogger("/home/home/Desktop/Projects/gsuneido/lsp-server/loom/log.txt")
	logger.Println("Hey, I started!")

	writer := os.Stdout

	scanner := bufio.NewScanner(os.Stdin)
	scanner.Split(rpc.Split)

	state := analysis.NewState()

	for scanner.Scan() {
		msg := scanner.Bytes()
		method, contents, err := rpc.DecodeMessage(msg)

		if err != nil {
			logger.Printf("Got an error: %s", err)
			continue
		}
		handleMessage(logger, writer, state, method, contents)
	}
}

func handleMessage(logger *log.Logger, writer io.Writer, state analysis.State, method string, content []byte) {
	switch method {
	case "initialize":
		var request lsp.InitializeRequest
		if err := json.Unmarshal(content, &request); err != nil {
			logger.Println("Got an error for initialize request: ", err)
			return
		}

		logger.Printf("connected to %s %s", request.Params.ClientInfo.Name, request.Params.ClientInfo.Version)

		msg := lsp.NewInitializeResponse(request.ID)
		writeResponseMessage(writer, msg)
		logger.Println("Sent initialize response")

	case "textDocument/didOpen":
		var request lsp.DidOpenTextDocumentNotification
		if err := json.Unmarshal(content, &request); err != nil {
			logger.Println("Got an error for didOpen request: ", err)
			return
		}

		state.OpenDocument(request.Params.TextDocument.URI, request.Params.TextDocument.Text)

		logger.Printf("Opened document: %s", request.Params.TextDocument.URI)
		logger.Println(request.Params.TextDocument.Text)

	case "textDocument/didChange":
		var request lsp.TextDocumentDidChangeNotification
		if err := json.Unmarshal(content, &request); err != nil {
			logger.Println("Got an error for didChange request: ", err)
			return
		}

		logger.Printf("Changed document: %s", request.Params.TextDocument.URI)
		logger.Println(request.Params.ContentChanges[0].Text)

		state.DidChangeCount += 1
		logger.Printf("Change count: %d", state.DidChangeCount)

		for _, change := range request.Params.ContentChanges {
			state.UpdateDocument(request.Params.TextDocument.URI, change.Text)
		}

	case "textDocument/inlayHint":
		var request lsp.InlayHintRequest
		if err := json.Unmarshal(content, &request); err != nil {
			logger.Println("Got an error for inlayHint request: ", err)
			return
		}

		logger.Printf("Got inlay hint request for %s at %d (%d)", request.Params.TextDocumentURI, request.Params.Range.Start.Line, request.Params.Range.Start.Character)

		// sleep for a bit
		time.Sleep(2 * time.Second)

		pos := lsp.Position{Line: 5, Character: 19}
		label := ": Admin"
		ih_member := lsp.NewInlayHint(pos, label)

		inlay_hints := []lsp.InlayHint{
			ih_member,
		}

		msg := lsp.NewInlayHintResult(request.ID, inlay_hints)
		writeResponseMessage(writer, msg)
		logger.Println("Sent inlay hint response")

	case "textDocument/diagnostic":
		var request lsp.DocumentDiagnosticRequest
		if err := json.Unmarshal(content, &request); err != nil {
			logger.Println("Got an error for publishDiagnostics request: ", err)
			return
		}
		logger.Printf("Got diagnostics request for %s", request.Params.TextDocument.URI)

		// sleep for a bit
		time.Sleep(2 * time.Second)

		diag0 := lsp.NewDiagnostic(lsp.Range{
			Start: lsp.Position{Line: 25, Character: 0},
			End:   lsp.Position{Line: 25, Character: 21}},
			"Type Mismatch: type Admin is not assignable to type User")

		diag1 := lsp.NewDiagnostic(lsp.Range{
			Start: lsp.Position{Line: 7, Character: 8},
			End:   lsp.Position{Line: 7, Character: 20},
		},
			"Does not match literal of type Currency")
		_ = diag1

		all_diags := []lsp.Diagnostic{
			diag0,
		}

		report := lsp.NewDocumentDiagnosticReport(all_diags)

		var reply lsp.DocumentDiagnosticResponse
		reply = lsp.NewDocumentDiagnosticReportResponse(request.ID, report)

		writeResponseMessage(writer, reply)
		logger.Println("Sent diagnostics response")

	default:
		logger.Println("[unhandled]: ", method)
	}
}

func writeResponseMessage(writer io.Writer, msg any) {
	reply := rpc.EncodeMessage(msg)
	writer.Write([]byte(reply))
}

func getLogger(filename string) *log.Logger {
	logfile, err := os.OpenFile(filename, os.O_CREATE|os.O_TRUNC|os.O_WRONLY, 0666)
	if err != nil {
		panic("LOG file not found")
	}

	return log.New(logfile, "[loom]", log.Ldate|log.Ltime|log.Lshortfile)
}
