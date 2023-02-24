import Stack from "./stack.js";
import { ANATOMICAL_NAMES } from "./constants.js";

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
// needs to be less than or equal to particle size for more precise selection
rayCaster.params.Points.threshold = 0.2;
// Normalized x, y coordinates of the user's mouse cursor in respect to the window
let mouse = new THREE.Vector2();

const pointStack = new Stack();

$(document).ready(function () {
  console.log(ANATOMICAL_NAMES[0]);
  window.addEventListener("resize", onWindowResize, false);
  window.addEventListener("keypress", onKeyPress, false);
  window.addEventListener("click", onClick, false);

  rawData = JSON.parse(data);
  document.body.appendChild(renderer.domElement);

  processRawData();
  scene.add(light);
  animate();
});

function animate() {
  controls.update();
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}

function processRawData() {
  for (let i = 0; i < rawData.length; i++) {
    positionPoints.push(rawData[i][0], rawData[i][1], rawData[i][2]);
    let color = new THREE.Color();
    color.setRGB(0.5, 0.92, 0.1);
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
    if (!pointStack.isEmpty()) {
      const sphereRemove = pointStack.pop();
      scene.remove(sphereRemove);
      // update the UI
      const promptElement = document.getElementById("point_cur");
      promptElement.innerHTML = ANATOMICAL_NAMES[pointStack.getSize()];
    }
  }
}

function onWindowResize() {
  camera.aspect = renderWidth / renderHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(renderWidth, renderHeight);
  animate();
}

function onClick(e) {
  if (e.shiftKey) {
    e.preventDefault();

    const offset = $("canvas").offset();
    mouse.x = ((e.clientX - offset.left) / renderWidth) * 2 - 1;
    mouse.y = -((e.clientY - offset.top) / renderHeight) * 2 + 1;

    rayCaster.setFromCamera(mouse, camera);
    const intersects = rayCaster.intersectObject(particles, false);
    if (intersects.length > 0 && pointStack.getSize() < 4) {
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
      pointStack.push(sphereMesh);
      scene.add(sphereMesh);
      // update the UI with js
      const promptElement = document.getElementById("point_cur");
      promptElement.innerHTML = ANATOMICAL_NAMES[pointStack.getSize()];
    }
  }
}
