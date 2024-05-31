use core::panic;

use hashbrown::HashMap;
use uuid::Uuid;
use crate::{lexer::Token, typekind::{FnKind, TypeKind}};



#[derive(Debug)]
pub struct NameSpace {
    issued: HashMap<String, Uuid>,
}

impl NameSpace {
    pub fn new() -> Self {
        NameSpace {
            issued: HashMap::new(),
        }
    }

    pub fn issue(&mut self, fn_name: &str, var_name: &str) -> Uuid {
        let name = fn_name.to_string() + "_" + var_name;
        let value = self.issued.get(&name);

        match value {
            Some(s) => {
                s.clone()
            }
            None => {
                let id = Uuid::new_v4();
                self.issued.insert(name, id);
                id
            }
        }

    }
}
#[derive(Debug)]
pub struct Stack<T> {
    stack: Vec<T>,
}

impl<T> Stack<T> {
    pub fn new() -> Self {
        Stack {
            stack: Vec::new(),
        }
    }

    pub fn push(&mut self, item: T) {
        self.stack.push(item);
    }

    pub fn pop(&mut self) -> Option<T> {
        self.stack.pop()
    }

    pub fn len(&self) -> usize {
        self.stack.len()
    }

    pub fn peek(&self) -> Option<&T> {
        self.stack.last()
    }

    pub fn is_empty(&self) -> bool {
        self.stack.is_empty()
    }
}

#[allow(non_camel_case_types)]
#[derive(Debug, Clone)]
pub enum ByteCode {
    CREATE_NODE(Uuid, TypeKind),
    SET_ARGUMENT(Uuid, Uuid),
}

#[derive(Debug)]
pub struct VirtualMachine {
    name: String,
    stack: Stack<Uuid>,
    namespace: NameSpace,
    bytecode: Vec<ByteCode>,
    stream: Vec<Token>,
    context: HashMap<String, usize>,
}

impl VirtualMachine {
    pub fn new(name: String, stream: Vec<Token>) -> Self {
        VirtualMachine {
            name,
            stack: Stack::new(),
            namespace: NameSpace::new(),
            bytecode: Vec::new(),
            stream,
            context: HashMap::new(),
        }
    }

    pub fn add_function_argument(&mut self, name: &str, idx: usize) {
        self.context.insert(name.to_string(), idx);
    }

    pub fn get_function_argument(&self, name: &str) -> Option<usize> {
        self.context.get(name).map(|x| x.clone())
    }

    pub fn bytecode_len(&self) -> usize {
        self.bytecode.len()
    }

    pub fn stack_len(&self) -> usize {
        self.stack.len()
    }

    pub fn get_id(&mut self, idx: usize) -> Uuid {
        let token = &self.stream[idx].clone();

        match token {
            Token::Identifier(n) => {
                self.namespace.issue(&self.name, n)
            },
            Token::Keyword(k) => {
                self.namespace.issue(&self.name, &(k.to_string() + "_" + &idx.to_string()))
            }
        }
    }

}

impl Into<Vec<ByteCode>> for VirtualMachine {

    fn into(mut self) -> Vec<ByteCode> {
        let stream = self.stream.clone(); 

        let ip: usize = 0;
        let mut bytecode: Vec<ByteCode> = Vec::new();

        // populate namespace
        for (x, i) in stream.iter().enumerate() {
            match i {
                Token::Keyword(k) => {
                    self.namespace.issue(&self.name, &(k.to_string() + "_" + &x.to_string()));
                },
                Token::Identifier(n) => {
                    self.namespace.issue(&self.name, n);
                }
            }
        }

        // to_bytecode logic
        for idx in 0..stream.len() {
            let tok = &stream[idx].clone();
            match tok {
                Token::Identifier(n) => {
                    bytecode.push(ByteCode::CREATE_NODE(self.namespace.issue(&self.name, n), TypeKind::Unknown));
                },
                Token::Keyword(f) => {
                    match f {
                        FnKind::Return => {
                            let return_id = self.get_id(idx);
                            let arg_id = self.get_id(idx + 1);

                            bytecode.push(ByteCode::CREATE_NODE(return_id, TypeKind::InBuilt(FnKind::Return)));
                            bytecode.push(ByteCode::SET_ARGUMENT(return_id, arg_id));
                        },
                        FnKind::Call => {
                            let call_id = self.get_id(idx);
                            let num_args = self.context.get(&self.name).unwrap();
                        }
                        _ => {
                            eprintln!("Unknown keyword: {:?}", f);
                            panic!()
                        }
                    }
                }
            }
        }

        bytecode
    }
    
}
