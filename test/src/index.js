import React from 'react'
import ReactDOM from 'react-dom'
import App from './App'
import WebFont from 'webfontloader'
import './index.css'

WebFont.load({
  google: {
    families: ['Architects Daughter', 'Open Sans:400', 'Rowdies:300,400']
  },
});

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);



// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
