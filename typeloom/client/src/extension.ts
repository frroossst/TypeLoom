import { createConnection, ProposedFeatures } from 'vscode-languageserver';

// Create a connection to the server
const connection = createConnection(ProposedFeatures.all);

// Initialize the connection
connection.listen();

// Request type hints at a specific position
const documentUri = 'file:///path/to/your/file.txt'; // Replace with the actual URI
const position = { line: 10, character: 5 }; // Replace with the actual position
connection.sendRequest('getTypeHints', {
  textDocument: { uri: documentUri },
  position: position,
}).then((typeHints) => {
  // Here, you'd update the editor UI with the received type hints
  console.log('Received type hints:', typeHints);
});
