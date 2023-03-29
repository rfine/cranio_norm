import { ANATOMICAL_NAMES, ANATOMICAL_POINT_COUNT } from "./constants.js";

const renderWidth = window.innerWidth * 0.7;
const renderHeight = window.innerHeight * 0.7;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  renderWidth / renderHeight,
  0.1,
  1000
);
camera.position.x = 200;

const renderer = new THREE.WebGLRenderer();

renderer.setSize(renderWidth, renderHeight);

const geometryPoints = new THREE.BufferGeometry();

let rawData = [];
let positionPoints = [];
let colors = [];

let particles = new THREE.Points();

let particleMaterial = new THREE.PointsMaterial({
  size: 0.3,
  vertexColors: true,
});

const controls = new THREE.OrbitControls(camera, renderer.domElement);
const light = new THREE.AmbientLight(0x404040);

// point selection variables
// emit a ray from the camera to the user cursor
const rayCaster = new THREE.Raycaster();
// value less than or equal to particle size
rayCaster.params.Points.threshold = 0.2;
// Normalized x, y coordinates of the user's mouse cursor in respect to the window
let mouse = new THREE.Vector2();

const pointsList = [];
let indexList = [];

let curIndex = 0;

$(document).ready(function () {
  window.addEventListener("resize", onWindowResize, false);
  window.addEventListener("keypress", onKeyPress, false);
  window.addEventListener("click", onClickCanvas, false);

  const btnNext = document.getElementById("nav-next-btn");
  btnNext.addEventListener("click", onClickNext, false);
  const btnPrev = document.getElementById("nav-prev-btn");
  btnPrev.addEventListener("click", onClickPrev, false);
  btnPrev.disabled = true;

  const subBtn = document.getElementById("submit-btn");
  subBtn.addEventListener("click", onClickSubmit, false);

  rawData = JSON.parse(data);
  createPointsList(rawData.length);
  // TODO need to update to have more control on where canvas is within the dom
  document.body.appendChild(renderer.domElement);
  scene.add(light);

  processRawData(rawData[curIndex]);
  animate();
});

function animate() {
  controls.update();
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}
function createPointsList(size) {
  for (let i = 0; i < size; i++) {
    pointsList.push([]);
    indexList.push([]);
  }
}

function isValidCheck() {
  for (let i = 0; i < pointsList.length; i++) {
    if (pointsList[i].length != ANATOMICAL_POINT_COUNT) {
      document.getElementById("submit-btn").disabled = true;
      return;
    }
  }
  document.getElementById("submit-btn").disabled = false;
}

function processRawData(curData) {
  positionPoints = [];
  colors = [];
  for (let i = 0; i < curData.length; i++) {
    positionPoints.push(curData[i][0], curData[i][1], curData[i][2]);
    const color = new THREE.Color(0.5, 0.92, 0.1);
    colors.push(color.r, color.g, color.b);
  }
  geometryPoints.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(positionPoints, 3)
  );
  geometryPoints.setAttribute(
    "color",
    new THREE.Float32BufferAttribute(colors, 3)
  );
  particles = new THREE.Points(geometryPoints, particleMaterial);
  scene.add(particles);
}

// windowEventListener impl
function onKeyPress(e) {
  if (e.key == "r") {
    if (pointsList[curIndex].length > 0) {
      const sphereRemove = pointsList[curIndex].pop();
      scene.remove(sphereRemove);
      updateText();
    }
  }
}

function onWindowResize() {
  camera.aspect = renderWidth / renderHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(renderWidth, renderHeight);
  animate();
}

function onClickCanvas(e) {
  if (e.shiftKey) {
    e.preventDefault();

    const offset = $("canvas").offset();
    mouse.x = ((e.clientX - offset.left) / renderWidth) * 2 - 1;
    mouse.y = -((e.clientY - offset.top) / renderHeight) * 2 + 1;

    rayCaster.setFromCamera(mouse, camera);
    const intersects = rayCaster.intersectObject(particles, false);
    if (intersects.length > 0 && pointsList[curIndex].length < 4) {
      // TODO is this index matching that of the data?
      const idx = intersects[0].index;
      const sphereGeo = new THREE.SphereGeometry(3, 30, 30);
      const sphereMat = new THREE.MeshBasicMaterial({ color: 0xffff00 });
      const sphereMesh = new THREE.Mesh(sphereGeo, sphereMat);
      const intersectionPoint = new THREE.Vector3(
        geometryPoints.attributes.position.getX(idx),
        geometryPoints.attributes.position.getY(idx),
        geometryPoints.attributes.position.getZ(idx)
      );
      sphereMesh.position.copy(intersectionPoint);
      pointsList[curIndex].push(sphereMesh);
      indexList[curIndex].push(idx);
      scene.add(sphereMesh);
      // update the UI with js
      updateText();
      isValidCheck();
    }
  }
}

function onClickNext() {
  removeScenePoints();
  curIndex++;
  processRawData(rawData[curIndex]);
  addScenePoints();
  updateText();

  if (curIndex >= rawData.length - 1) {
    const btnNext = document.getElementById("nav-next-btn");
    btnNext.disabled = true;
  }
  const btnPrev = document.getElementById("nav-prev-btn");
  btnPrev.disabled = false;
}

function onClickPrev() {
  removeScenePoints();
  curIndex--;
  processRawData(rawData[curIndex]);
  addScenePoints();
  updateText();

  if (curIndex <= 0) {
    const btnPrev = document.getElementById("nav-prev-btn");
    btnPrev.disabled = true;
  }

  const btnNext = document.getElementById("nav-next-btn");
  btnNext.disabled = false;
}

function onClickSubmit() {
  let form = document.getElementById("form-points");

  let ret = [];
  for (let i = 0; i < pointsList.length; i++) {
    const skullPoints = pointsList[i];
    ret[i] = [];
    for (let j = 0; j < skullPoints.length; j++) {
      console.log(indexList[i][j]);
      console.log(pointsList[i][j].position);
      ret[i].push(indexList[i][j]);
    }
  }

  console.log(ret);
  const retJSON = JSON.stringify(ret);

  let input = document.createElement("input");
  input.setAttribute("name", "index");
  input.setAttribute("value", retJSON);
  input.setAttribute("type", "hidden");
  form.appendChild(input);
  // const formData = new FormData(form);
  // for (var pair of formData.entries()) {
  //   console.log(pair[0] + ", " + pair[1]);
  // }
  form.submit();
}

function removeScenePoints() {
  for (let i = 0; i < pointsList[curIndex].length; i++) {
    const sphereRemove = pointsList[curIndex][i];
    scene.remove(sphereRemove);
  }
}

function addScenePoints() {
  for (let i = 0; i < pointsList[curIndex].length; i++) {
    const sphereAdd = pointsList[curIndex][i];
    scene.add(sphereAdd);
  }
  isValidCheck();
}

function updateText() {
  const promptElement = document.getElementById("point-cur");
  promptElement.innerHTML = ANATOMICAL_NAMES[pointsList[curIndex].length];
}
