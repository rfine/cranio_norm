const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.z = 1;

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);

const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });

const geometryPoints = new THREE.BufferGeometry();

var rawData = [];
var positionPoints = [];

var materialTest = new THREE.PointsMaterial({
  size: 0.1,
  color: 0xff0000,
});

const controls = new THREE.OrbitControls(camera, renderer.domElement);

$(document).ready(function () {
  rawData = JSON.parse(data);

  document.body.appendChild(renderer.domElement);
  processRawData();
  // scene.add(cube);
  animate();
});

function animate() {
  controls.update();
  requestAnimationFrame(animate);

  renderer.render(scene, camera);
}

function processRawData() {
  for (i = 0; i < rawData.length; i++) {
    positionPoints.push(rawData[i][0], rawData[i][1], rawData[i][2]);
  }
  geometryPoints.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(positionPoints, 3)
  );
  particles = new THREE.Points(geometryPoints, materialTest);
  scene.add(particles);
}
