package lsp

type InitializeRequest struct {
	Request
	Params InitializeRequestParams `json:"params"`
}

type InitializeRequestParams struct {
	ClientInfo *ClientInfo `json:"clientInfo"`
}

type ClientInfo struct {
	Name    string `json:"name"`
	Version string `json:"version"`
}

type InitializeResponse struct {
	Response
	Result InitializeResponseResult `json:"result"`
}

type InitializeResponseResult struct {
	Capabilities ServerCapabilities `json:"capabilities"`
	ServerInfo   ServerInfo         `json:"serverInfo"`
}

type ServerCapabilities struct {
	TextDocumentSync int `json:"textDocumentSync"`

	InlayHintProvider bool `json:"inlayHintProvider"`

	DiagnosticProvider DiagnosticOptions `json:"diagnosticProvider"`
}

type DiagnosticOptions struct {
	InterFileDependencies bool `json:"interFileDependencies"`
	WorkspaceDiagnostics  bool `json:"workspaceDiagnostics"`
}

type ServerInfo struct {
	Name    string `json:"name"`
	Version string `json:"version"`
}

func NewInitializeResponse(id int) InitializeResponse {
	return InitializeResponse{
		Response: Response{
			RPC: "2.0",
			ID:  &id,
		},
		Result: InitializeResponseResult{
			Capabilities: ServerCapabilities{
				TextDocumentSync:  1, // Full sync
				InlayHintProvider: true,
				DiagnosticProvider: DiagnosticOptions{
					InterFileDependencies: false,
					WorkspaceDiagnostics:  true,
				},
			},
			ServerInfo: ServerInfo{
				Name:    "Loom",
				Version: "0.0.1",
			},
		},
	}
}
