use crate::{bytecode::VirtualMachine, parser::Parser, typekind::FnKind};

#[derive(Debug, Clone, PartialEq, serde::Serialize, serde::Deserialize)]
pub enum Token {
    Keyword(FnKind),
    Identifier(String),
}

#[derive(Debug, Clone)]
pub struct Lexer {
    name: String,
    args: Vec<String>,
    src: Vec<String>,
    line: usize,
}

impl Lexer {
    pub fn new(src: &str) -> Self {

        let src: Vec<String> = src.trim().split_terminator('\n').map(|x| x.to_string()).collect();

        let mut p = Parser::new(src[0].as_str());

        let name = p.consume_identifier().unwrap();
        p.consume_whitespace();
        p.consume_keyword("Function").unwrap();
        p.consume_brace('(').unwrap();

        // split till end of line by ,
        let args = p.remaining().split_terminator(',').map(|x| x.trim().to_string()).collect::<Vec<String>>();

        let mut src: Vec<String> = src[1..].iter().map(|x| x.trim().to_string()).filter(|x| x.len() > 0).collect();

        // remove ) from the last element of src
        // this is a remnant of the Function closing bracket
        let last = src.len() - 1;
        let last_elem = src[last].clone();
        src[last] = last_elem[..last_elem.len()-1].to_string();

        Self {
            name,
            args,
            src,
            line: 0,
        }
    }

    pub fn debug(&self) {
        let src = &self.src[self.line..];
        dbg!(src);
    }

    pub fn len(&self) -> usize {
        self.src.len()
    }

    pub fn name(&self) -> String {
        self.name.clone()
    }

    pub fn arguments(&self) -> Vec<String> {
        self.args.clone()
    }

    pub fn tokenize(&mut self) {
        self.src = self.src.iter().map(|x| x.split_whitespace()).flatten().map(|x| x.to_string()).collect();
    }

    pub fn next(&mut self) -> Option<Vec<Token>> {
        let mut tokens: Vec<Token> = Vec::new();

        if self.line >= self.src.len() {
            return None;
        }

        let line = self.src[self.line].clone();
        let mut p = Parser::new(line.as_str());

        while let Some(tok) = p.next() {
            match tok.as_str() {
                "Return" => {
                    tokens.push(Token::Keyword(FnKind::Return));
                },
                "Add" => {
                    tokens.push(Token::Keyword(FnKind::Add));
                },
                "Eq" => {
                    tokens.push(Token::Keyword(FnKind::Eq));
                },
                "Is" => {
                    tokens.push(Token::Keyword(FnKind::Is));
                },
                "Call" => {
                    tokens.push(Token::Keyword(FnKind::Call));
                }
                "Binary" | "Unary" | "Nary" => {
                    continue;
                },
                "" => {
                    continue;
                },
                _ => {
                    tokens.push(Token::Identifier(tok.to_string()));
                }
            }
        }

        self.line += 1;

        if tokens.len() > 0 {
            Some(tokens)
        } else {
            None
        }
    }
}

impl Into<Vec<Token>> for Lexer {
    fn into(mut self) -> Vec<Token> {
        let mut byc_tokens: Vec<Token> = Vec::new();

        while let Some(tokens) = self.next() {
            for token in tokens {
                byc_tokens.push(token);
            }
        }

        byc_tokens
    }
}

impl Into<VirtualMachine> for Lexer {

    fn into(self) -> VirtualMachine {
        let name = self.name.clone();
        let tokens: Vec<Token> = self.into();

        VirtualMachine::new(name, tokens)
    }
}
