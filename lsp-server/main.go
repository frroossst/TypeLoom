package main

import (
	"fmt"
	"os"

	"encoding/json"

	"github.com/apmckinlay/gsuneido/compile"
)

func main() {

	/*
		1. Mark x as unknown (as it wont be known in the first pass)
		2. Mark num as unknown + Number (123)
		3. Evaluate x to be Number (as only then could it be added to 123)
		4. Evaluate num to be Number
		5. Throw error as Number is not callable
	*/
	src := `class {
			x: 0
			msg: "hello"
			myMessage: ""
		currencyTypeAlias()
			{
			u = "USD"
			// nu = "usd"
			// ou = "other"
			}
		GetUserAuth(usr)
			{
			return false
			}
		GetUserAuthCall()
			{
			x = Object(name: "John", age: 25)
			GetUserAuth(x)
			}
		Get() { return Object(99, 68, ans: Hello(1, 2), numx: .x, strmsg: .msg) }
		Hello(x, y) { return x + y }
		pvt_foo() { return .x }
		originalTestFunc(x, y, z)
			{
			num = x + 123
			num++
			if Number?(x) and Number?(y)
				{
				abc = x + y + z + num
				}
			else
				{
				// num()
				}
			num2 = x + 1
			.qux()
			}
		JoinStrings(str) { .myMessage = .myMessage $ str }
		pvt_bar() { return .msg }
		SetX(x) { .x = x }
		SetMsg(msg) { .msg = msg }
		AddBreak() { return x + 123 }
		ParenthesisTest(x, y, z) { return (x + y) * z }
		// simpleTypeAlias(a) { a = "thisShouldNotAssign" }
		}`

	/*
		 * Discarded Lines

		DeletePriority(a, b) { return 12345679 - a - b }
		ParameterMismatch(x) { x = "IAmAString" $ "adfs" }
		DeletePriority(a, b) { return 12345679 + '-a' - b } // this works
		IncorrectNumberOfParamsTyped(x, y) { return x + y }
		SameVarID(x)
			{
			x = "123"
			x = 123
			y = x + 123
			y = "hello"
			z = 123.456
			x = z
			y = z
			z = x + y
			}
	*/

	src = `class {
        IsOdd(num) {
            if (num % 2 is 0) {
                return false
            }
            else {
                return true
            }
        }
		Compose_f(f)
	        {
	        return f
	        }
	    Compose_g(g)
	        {
	        return g
	        }

	    Compose_x(f, g, x)
	        {
	        return f(g(x))
	        }
	    Double(x)
	        {
	        return x * 2
	        }

	    Increment(x)
	        {
	        return x + 1
	        }
		}
	`

	src = `class {
		Add(x, y) {
			a = x + y
			return a
		}}
	`

	fmt.Println("src:", src)
	fmt.Println()
	fmt.Println("compiled:", compile.AstParser(src).Const())
	fmt.Println()

	p := compile.AstParser(src)
	cl := p.TypeClass()

	fmt.Println("=== Class ===")
	fmt.Println("class ", cl.Name, " from ", cl.Base)
	fmt.Println("\tAttributes:")
	for name, attr := range cl.Attributes {
		a := attr[0]
		fmt.Println("\t", name, ":")
		fmt.Println("\t\t", a.Value)
		fmt.Println("\t\t", a.Tag)
		fmt.Println("\t\t", a.Type_t)
		fmt.Println()
	}
	fmt.Println("\tMethods:")
	for _, method := range cl.Methods {
		m := method[0]
		fmt.Println("\t", m.Name, "(", m.Parameters, ")")
		for _, stmt := range m.Body {
			fmt.Println("\t\t", stmt)
		}
		fmt.Println()
	}

	// convert to json
	jsonData, err := json.Marshal(cl)
	if err != nil {
		panic(err)
	}

	// delete file if it exists
	if _, err := os.Stat("ast.json"); err == nil {
		err = os.Remove("ast.json")
		if err != nil {
			panic(err)
		}
	}
	// write json data to file
	fobj, err := os.OpenFile("ast.json", os.O_RDWR|os.O_CREATE, 0755)
	if err != nil {
		panic(err)
	}
	defer fobj.Close()

	_, err = fobj.WriteString(string(jsonData))
	if err != nil {
		panic(err)
	}

	if _, err := os.Stat("ast.loom"); err == nil {
		err = os.Remove("ast.loom")
		if err != nil {
			panic(err)
		}
	}
	// write json data to file
	fobj2, err := os.OpenFile("ast.loom", os.O_RDWR|os.O_CREATE, 0755)
	if err != nil {
		panic(err)
	}
	defer fobj2.Close()

	astSrc := compile.AstParser(src).Const()
	_, err = fobj2.WriteString(astSrc.String())
	if err != nil {
		panic(err)
	}

}
