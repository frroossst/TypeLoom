package lsp

type DocumentDiagnosticRequest struct {
	Request
	Params DocumentDiagnosticParams `json:"params"`
}

type DocumentDiagnosticParams struct {
	TextDocument TextDocumentIdentifier `json:"textDocument"`
}

type DocumentDiagnosticReport = RelatedFullDocumentDiagnosticReport
type RelatedFullDocumentDiagnosticReport = FullDocumentDiagnosticReport
type DocumentDiagnosticResponse struct {
	Response
	Result DocumentDiagnosticReport `json:"result"`
}

func NewDocumentDiagnosticReportResponse(id int, report RelatedFullDocumentDiagnosticReport) DocumentDiagnosticResponse {
	return DocumentDiagnosticResponse{
		Response: Response{
			RPC: "2.0",
			ID:  &id,
		},
		Result: report,
	}
}

func NewDocumentDiagnosticReport(diogs []Diagnostic) RelatedFullDocumentDiagnosticReport {
	return RelatedFullDocumentDiagnosticReport{
		Kind: "full",
		Items: diogs,
	}

}

func NewDiagnostic(range_ Range, message string) Diagnostic {
	return Diagnostic{
		Range:   range_,
		Message: message,
	}
}

type DocumentDiagnosticReportKind string // "full"
type FullDocumentDiagnosticReport struct {
	Kind DocumentDiagnosticReportKind `json:"kind"`
	Items []Diagnostic                `json:"items"`
}

type Diagnostic struct {
	Range    Range  `json:"range"`
	Message  string `json:"message"`
}
