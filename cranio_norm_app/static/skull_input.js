const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.z = 5;

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);

const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);

const geometryPoints = new THREE.BufferGeometry();

var rawData = [];

var materialTest = new THREE.PointsMaterial({
  size: 0.01,
  vertexColors: true,
});

$(document).ready(function () {
  rawData = JSON.parse(data);
  console.log(typeof rawData);
  console.log(rawData);

  document.body.appendChild(renderer.domElement);
  // scene.add(cube);
  animate();
});

function animate() {
  requestAnimationFrame(animate);

  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;

  renderer.render(scene, camera);
}

function processRawData() {
  geometryPoints.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(rawData, 3)
  );
  particles = new THREE.Points(geometryPoints, materialTest);
  scene.add(particles);
}
