// server.js

// Import the required modules
import { createConnection, TextDocuments, ProposedFeatures } from 'vscode-languageserver/node';
import { TextDocument } from 'vscode-languageserver-textdocument';

// Create a connection for the server
const connection = createConnection(ProposedFeatures.all);

// Create a simple text document manager
const documents: TextDocuments<TextDocument> = new TextDocuments(TextDocument);

// Listen for open, change and close text document events
documents.listen(connection);

// Print the source code of any opened document
documents.onDidOpen((event) => {
    console.log('Document opened: ' + event.document.uri);
    console.log('Source code:\n' + event.document.uri.toString());
});

// Print any changes made to the document
documents.onDidChangeContent((event) => {
    console.log('Document changed: ' + event.document.uri);
    console.log('Source code:\n' + event.document.uri.toString());
});

// Print when the document is closed
documents.onDidClose((event) => {
    console.log('Document closed: ' + event.document.uri.toString());
});

// Listen on the connection
connection.listen();
