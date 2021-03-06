package models

import (
	"github.com/podhmo/maperr"
	"encoding/json"
)

// this file is generated by egoist.generators.structkit

type Person struct {
	Name string `json:"name"`
	Age int `json:"age"`
	Followings [][]Person `json:"followings"`
	Followings2 [][]*Person2 `json:"followings2"`
	Groups map[string]map[string]Person `json:"groups"`
	Groups2 map[string]map[string]*Person2 `json:"groups2"`
}

func (p *Person) UnmarshalJSON(b []byte) error {
	var err *maperr.Error

	// loading internal data
	var inner struct {
		Name *string `json:"name"`// required
		Age *int `json:"age"`// required
		Followings *json.RawMessage `json:"followings"`// required
		Followings2 *json.RawMessage `json:"followings2"`// required
		Groups *json.RawMessage `json:"groups"`// required
		Groups2 *json.RawMessage `json:"groups2"`// required
	}
	if rawErr := json.Unmarshal(b, &inner); rawErr != nil  {
		return err.AddSummary(rawErr.Error())
	}

	// binding field value and required check
	{
		if inner.Name != nil  {
			p.Name = *inner.Name
		} else  {
			err = err.Add("name", maperr.Message{Text: "required"})
		}
		if inner.Age != nil  {
			p.Age = *inner.Age
		} else  {
			err = err.Add("age", maperr.Message{Text: "required"})
		}
		if inner.Followings != nil  {
			p.Followings = [][]Person{}
			if rawerr := json.Unmarshal(*inner.Followings, &p.Followings); rawerr != nil  {
				err = err.Add("followings", maperr.Message{Error: rawerr})
			}
		} else  {
			err = err.Add("followings", maperr.Message{Text: "required"})
		}
		if inner.Followings2 != nil  {
			p.Followings2 = [][]*Person2{}
			if rawerr := json.Unmarshal(*inner.Followings2, &p.Followings2); rawerr != nil  {
				err = err.Add("followings2", maperr.Message{Error: rawerr})
			}
		} else  {
			err = err.Add("followings2", maperr.Message{Text: "required"})
		}
		if inner.Groups != nil  {
			p.Groups = map[string]map[string]Person{}
			if rawerr := json.Unmarshal(*inner.Groups, &p.Groups); rawerr != nil  {
				err = err.Add("groups", maperr.Message{Error: rawerr})
			}
		} else  {
			err = err.Add("groups", maperr.Message{Text: "required"})
		}
		if inner.Groups2 != nil  {
			p.Groups2 = map[string]map[string]*Person2{}
			if rawerr := json.Unmarshal(*inner.Groups2, &p.Groups2); rawerr != nil  {
				err = err.Add("groups2", maperr.Message{Error: rawerr})
			}
		} else  {
			err = err.Add("groups2", maperr.Message{Text: "required"})
		}
	}

	return err.Untyped()
}

type Person2 struct {
	Name string `json:"name"`
}

func (p *Person2) UnmarshalJSON(b []byte) error {
	var err *maperr.Error

	// loading internal data
	var inner struct {
		Name *string `json:"name"`// required
	}
	if rawErr := json.Unmarshal(b, &inner); rawErr != nil  {
		return err.AddSummary(rawErr.Error())
	}

	// binding field value and required check
	{
		if inner.Name != nil  {
			p.Name = *inner.Name
		} else  {
			err = err.Add("name", maperr.Message{Text: "required"})
		}
	}

	return err.Untyped()
}