package main
// this packaage is auto generated

import (
	"fmt"
	"flag"
	"os"
	"log"
)

type Option struct {
	Name string
}


func main()  {
	opt := &Option{}
	cmd := flag.NewFlagSet("hello", flag.ContinueOnError)

	cmd.StringVar(&opt.Name, "name", "foo", "name of person")

	if err := cmd.Parse(os.Args[1:]); err != nil {
		if err != flag.ErrHelp {
			cmd.Usage()
		}
		os.Exit(1)
	}
	if err := run(opt); err != nil {
		log.Fatalf("!!%+v", err)
	}
}

func run(opt *Option) error {
	fmt.Printf("hello %s\n", opt.Name)
	return nil
}