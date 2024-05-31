package lsp

type InlayHintRequest struct {
	Request
	Params InlayHintParams `json:"params"`
}

type Range struct {
	Start Position `json:"start"`
	End   Position `json:"end"`
}

type Position struct {
	Line      int `json:"line"`
	Character int `json:"character"`
}

type InlayHintParams struct {
	TextDocumentURI string `json:"textDocumentUri"`
	Range           Range  `json:"range"`
}

type InlayHint struct {
	Position Position `json:"position"`
	Label    string   `json:"label"`
}

type InlayHintResponse struct {
	Response
	Result []InlayHint `json:"result"`
}

func NewInlayHint(position Position, lable string) InlayHint {
	return InlayHint{
		Position: position,
		Label:    lable,
	}

}

func NewInlayHintResult(id int, inlayHints []InlayHint) InlayHintResponse {
	return InlayHintResponse{
		Response: Response{
			RPC: "2.0",
			ID: &id,
		},
		Result: inlayHints,
	}
}
