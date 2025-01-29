import React from 'react';
import Header from './components/Header';
import TechStack from './components/TechStack';
import PitchDeckLink from './components/PitchDeckLink';
import './styles/App.css';

const App = () => {
  return (
    <div className="app">
      <Header />
      <TechStack />
      <PitchDeckLink />
    </div>
  );
};

export default App;
