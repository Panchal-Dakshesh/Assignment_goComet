import React, {Component} from 'react';
import {Switch, Route} from 'react-router-dom';
import "bootstrap/dist/css/bootstrap.min.css";
import './App.css';
// import Navbar from "./components/Navbar";
import Default from "./components/Default";
import Admin from './components/Admin';

class App extends Component {
  render() {
    return (
        <React.Fragment>
          <Switch>
              <Route exact path="/" component={Admin} />
              <Route component={Default} />
          </Switch>
        </React.Fragment>
    );
  }
}

export default App;