import { createContext, useContext, useState, useCallback } from 'react';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [stressMode, setStressMode] = useState(false);
  const [usingMock, setUsingMock] = useState(false);
  const [city, setCity] = useState('bengaluru');

  const toggleStress = useCallback(() => setStressMode(p => !p), []);

  return (
    <AppContext.Provider value={{ stressMode, toggleStress, usingMock, setUsingMock, city, setCity }}>
      {children}
    </AppContext.Provider>
  );
}

export const useApp = () => useContext(AppContext);
