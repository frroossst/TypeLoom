package analysis

type State struct {
	Documents      map[string]string
	DidChangeCount int
}

func NewState() State {
	return State{
		Documents:      map[string]string{},
		DidChangeCount: 0,
	}
}

func (s *State) OpenDocument(uri, text string) {
	s.Documents[uri] = text
}

func (s *State) UpdateDocument(uri string, text string) {
	s.Documents[uri] = text
}
