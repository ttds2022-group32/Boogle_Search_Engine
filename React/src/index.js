import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import Search from './Search';
import Logo from './Logo';
import Item from './Item';


ReactDOM.render(
  <React.StrictMode>
    <Logo />
    <Search />
  </React.StrictMode>,
  document.getElementById('root')
);
