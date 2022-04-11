import React, {Component} from 'react';
import {Switch, Route} from 'react-router-dom';
import "bootstrap/dist/css/bootstrap.min.css";
import './App.css';
import Error from "./components/Error";
import Blogs from './components/Blogs';

class App extends Component {
  render() {
    return (
        <React.Fragment>
          <Switch>
              <Route exact path="/" component={Blogs} />
              <Route component={Error} />
          </Switch>
        </React.Fragment>
    );
  }
}

export default App;