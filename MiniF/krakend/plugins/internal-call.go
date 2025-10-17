package main

import (
    "context"
    "encoding/json"
    "errors"
    "fmt"
    "io"
    "net/http"
    "net/url"
    "strconv"
)

// ModifierRegisterer is the symbol KrakenD looks for.
var ModifierRegisterer = registerer("internal-call")

type registerer string

// RegisterModifiers registers the modifier factory.
func (r registerer) RegisterModifiers(f func(
    name string,
    factory func(map[string]interface{}) func(interface{}) (interface{}, error),
    appliesToRequest bool,
    appliesToResponse bool,
)) {
    // Register as a request modifier only.
    f(string(r), r.modifierFactory, true, false)
    fmt.Println(string(r), "registered")
}

// modifierFactory creates the modifier function based on config.
func (r registerer) modifierFactory(cfg map[string]interface{}) func(interface{}) (interface{}, error) {
    authURL := "http://web:8000/api/users/auth/confirm-token/"
    if v, ok := cfg["auth_url"].(string); ok && v != "" {
        authURL = v
    }
    fmt.Println("Using auth_url:", authURL)

    return func(input interface{}) (interface{}, error) {
        req, ok := input.(RequestWrapper)
        if !ok {
            return nil, errors.New("unknown request type")
        }

        tokenHeaders := req.Headers()["Authorization"]
        if len(tokenHeaders) == 0 || tokenHeaders[0] == "" {
            return nil, &HTTPResponseError{Code: 401, Msg: "missing Authorization header"}
        }
        token := tokenHeaders[0]
        fmt.Println("InternalCall plugin triggered")
        fmt.Println("Incoming token:", token)

        client := &http.Client{}
        authReq, err := http.NewRequestWithContext(context.Background(), "GET", authURL, nil)
        if err != nil {
            return nil, &HTTPResponseError{Code: 500, Msg: err.Error()}
        }
        authReq.Header.Set("Authorization", token)

        resp, err := client.Do(authReq)
        if err != nil {
            return nil, &HTTPResponseError{Code: 500, Msg: err.Error()}
        }
        defer resp.Body.Close()

        if resp.StatusCode == 401 {
            return nil, &HTTPResponseError{Code: 401, Msg: "unauthorized"}
        }

        body, err := io.ReadAll(resp.Body)
        if err != nil {
            return nil, &HTTPResponseError{Code: 500, Msg: err.Error()}
        }
        data := map[string]interface{}{}
        if err := json.Unmarshal(body, &data); err != nil {
            return nil, &HTTPResponseError{Code: 500, Msg: err.Error()}
        }
        fmt.Printf("Response data: %+v\n", data)  // Debug log to see the exact response map

        // Handle user_id or uid, as float64 or string
        var uidStr string
        if val, ok := data["user_id"]; ok {
            switch v := val.(type) {
            case float64:
                uidStr = strconv.FormatFloat(v, 'f', 0, 64)
            case string:
                uidStr = v
            }
        } else if val, ok := data["uid"]; ok {
            switch v := val.(type) {
            case float64:
                uidStr = strconv.FormatFloat(v, 'f', 0, 64)
            case string:
                uidStr = v
            }
        }
        if uidStr != "" {
            req.Headers()["user-id"] = []string{uidStr}
            fmt.Println("Set user_id header to:", uidStr)  // Debug log
        } else {
            fmt.Println("No user_id or uid found in response")  // Debug log
        }

        if role, ok := data["role"].(string); ok {
            req.Headers()["role"] = []string{role}
            fmt.Println("Set role header to:", role)  // Debug log
        }

        return input, nil
    }
}

// RequestWrapper interface (required for type assertion).
type RequestWrapper interface {
    Params() map[string]string
    Headers() map[string][]string
    Body() io.ReadCloser
    Method() string
    URL() *url.URL
    Query() url.Values
    Path() string
}

// HTTPResponseError for custom error with status code.
type HTTPResponseError struct {
    Code int
    Msg  string
}

func (e *HTTPResponseError) Error() string {
    return e.Msg
}

func (e *HTTPResponseError) StatusCode() int {
    return e.Code
}

func main() {}  // Empty main is fine for plugins