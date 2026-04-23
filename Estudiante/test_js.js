const fs = require('fs');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

const html = fs.readFileSync('c:/Proyectos/FeriaFront/Estudiante/mis_favoritos.html', 'utf8');

const simulatedLocalStorage = {
  data: {},
  getItem(key) { return this.data[key] || null; },
  setItem(key, val) { this.data[key] = String(val); }
};

simulatedLocalStorage.setItem('favoritos', JSON.stringify([{
  id: 1, 
  title: "Test", 
  company: "Co", 
  modality: "Presencial"
}]));

const dom = new JSDOM(html, { 
    url: "http://localhost:5500/Estudiante/mis_favoritos.html",
    runScripts: "outside-only" 
});

const window = dom.window;
window.localStorage = simulatedLocalStorage;

const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);

if(scriptMatch) {
  let jsCode = scriptMatch[1];
  
  // Create a clean script by removing standard browser setup we mocked
  jsCode = jsCode.replace("const API_BASE", "var API_BASE");
  jsCode = jsCode.replace("const token = localStorage.getItem('token');", "");
  jsCode = jsCode.replace("if (!token) location.href = 'acceso_estudiante.html';", "");
  jsCode += "\ncargarFavoritos()";

  try {
    const fn = new window.Function(jsCode);
    fn();
    const container = window.document.getElementById('favorites-container');
    console.log("Container innerHTML:", container.innerHTML);
    
    if (container.innerHTML.includes('Test')) {
      console.log("ALL GOOD. It rendered!");
    } else {
      console.log("Empty container. Error in rendering logic.");
    }
    
  } catch(e) {
    console.error("RUNTIME ERROR:", e);
  }
}
