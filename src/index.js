// Takes the top-level react component and attaches it to the DOM.

import React from "react";
import ReactDOM from "react-dom";
import App from "./js/react/App";
import "semantic-ui-css/semantic.min.css";
// import "./scss/main.scss";

const contentWrapper = document.getElementById("react-entrypoint");

if (contentWrapper) {
    ReactDOM.render(<App />, contentWrapper);
}
