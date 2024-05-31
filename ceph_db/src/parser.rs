#[derive(Debug, Clone)]
pub struct Parser{
    src: String,
    pos: usize,
}

impl Parser {
    pub fn new(src: &str) -> Self {
        Self {
            src: src.to_string(),
            pos: 0,
        }
    }

    pub fn debug(&self) {
        let src = &self.src[self.pos..];
        dbg!(src);
    }

    pub fn remaining(&self) -> String {
        self.src[self.pos..].to_string()
    }

    pub fn len(&self) -> usize {
        self.src.len()
    }

    pub fn consume_whitespace(&mut self) {
        while self.pos < self.src.len() && self.src.chars().nth(self.pos).unwrap().is_whitespace() {
            self.pos += 1;
        }
    }

    pub fn consume_whitespace_or_brackets(&mut self) {
        self.consume_whitespace();
        while self.pos < self.src.len() && (self.src.chars().nth(self.pos).unwrap() == '(' || self.src.chars().nth(self.pos).unwrap() == ')') {
            self.pos += 1;
        }
    }

    pub fn consume_whitespace_no_newline(&mut self) {
        while self.pos < self.src.len() && self.src.chars().nth(self.pos).unwrap().is_whitespace() && self.src.chars().nth(self.pos).unwrap() != '\n' {
            self.pos += 1;
        }
    }

    pub fn consume_keyword(&mut self, keyword: &str) -> Result<(), String> {
        let keyword_len = keyword.len();
        if self.src[self.pos..].starts_with(keyword) {
            self.pos += keyword_len;
            Ok(())
        } else {
            Err(format!("Expected keyword: {}", keyword))
        }
    }

    pub fn consume_brace(&mut self, brace: char) -> Result<(), String> {
        self.consume_whitespace();
        if self.src.chars().nth(self.pos) == Some(brace) {
            self.pos += 1;
            Ok(())
        } else {
            Err(format!("Expected brace: {}", brace))
        }
    }

    pub fn parse_methods(&self) -> Vec<String> {

        let input = &self.src[self.pos..];
        let mut functions = Vec::new();
    
        let mut func = String::new();
        let lines: Vec<&str> = input.lines().collect();

        for line in lines {
            if line.trim() == "}" {
                break;
            }
            if line.contains("Function") {
                functions.push(func);
                func = String::new();
            }
            func.push_str(line);
            func.push_str("\n");
        }
        functions.push(func.clone());

        functions.retain(|x| x.len() > 0);

        functions
    }

    pub fn consume_identifier(&mut self) -> Result<String, String> {
        self.consume_whitespace();
        // identifier rules are similar to Python variables, alphanumeric and underscores
        let mut identifier = String::new();
        
        // read until colon
        while self.pos < self.src.len() {
            let c = self.src.chars().nth(self.pos).unwrap();
            if c.is_alphanumeric() || c == '_' {
                identifier.push(c);
                self.pos += 1;
            } else if c == ':' {
                self.pos += 1;
                break;
            } else if c == ',' {
                self.pos += 1;
                break;
            } else {
                break;
            }
        }

        return Ok(identifier);

    }

    fn parse_arguments(&mut self) -> Vec<String> {
        let mut args = Vec::new();

        loop {
            self.consume_whitespace_no_newline();
            let arg = self.consume_identifier().unwrap();
            args.push(arg.clone());

            self.consume_whitespace_no_newline();
            if self.src.chars().nth(self.pos) == Some(',') {
                self.pos += 1;
                dbg!(arg.clone());
                continue; // Consume the comma and continue to the next argument
            } else {
                break;
            }
        }

        args
    }

    pub fn parse_function(&mut self) -> Vec<String> {
        self.consume_whitespace();
        self.consume_keyword("Function").unwrap();

        self.consume_brace('(').unwrap();
        self.consume_whitespace();

        // consume arguments
        let args = self.parse_arguments();

        // self.consume_brace(')').unwrap();

        args
    }

    // returns either the next keyword, token, or identifier
    pub fn next(&mut self) -> Option<String> {
        // read until a space or newline or ( or ) is encountered
        let mut token = String::new();

        if self.pos >= self.src.len() {
            return None;
        }

        while self.pos < self.src.len() {
            let c = self.src.chars().nth(self.pos).unwrap();
            if c == '(' || c == ')' {
                self.pos += 1;
                break;
            }
            token.push(c);
            self.pos += 1;
        }

        Some(token)
    }

}
