# my-interpreter

Inspiration from https://craftinginterpreters.com/

This repository is side project to learn how programming languages are implemented.

I have implemented a simple interpreter for a simple language called `lox` in Python.

Features it supports:

- Arithmetic operations
  ```
    print 1 + 2 * 3;
    print (1 + 2) * 3;
    ```
- Variables
    ```
        var a = 10;
        print a;
    ```

- Control flow (if-else)
    ```
        if (a > 10) {
            print "a is greater than 10";
        } else {
            print "a is less than or equal to 10";
        }
    ```

- Loops (while and for)
    ```
        var a = 0;
        while (a < 10) {
            print a;
            a = a + 1;
        }

        for (var i = 0; i < 10; i = i + 1) {
            print i;
        }
    ```
- Functions
    ```
        fun add(a, b) {
            return a + b;
        }

        print add(1, 2);
    ```
- Closures
    ```
        fun outer() {
            var a = 10;
            fun inner() {
                print a;
            }
            return inner;
        }

        var f = outer();
        f();
    ```
- Recursion
    ```
        fun fib(n) {
            if (n <= 1) return n;
            return fib(n - 1) + fib(n - 2);
        }

        print fib(10);
    ```
- Classes
    ```
        class A {
            init(a) {
                this.a = a;
            }

            printA() {
                print this.a;
            }
        }

        var a = A(10);
        a.printA();
    ```
- Inheritance
    ```
        class A {
            init(a) {
                this.a = a;
            }

            printA() {
                print this.a;
            }
        }

        class B extends A {
            init(a, b) {
                super.init(a);
                this.b = b;
            }

            printB() {
                print this.b;
            }
        }

        var b = B(10, 20);
        b.printA();
        b.printB();
    ```