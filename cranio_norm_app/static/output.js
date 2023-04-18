const renderWidth = window.innerWidth * 0.7;
const renderHeight = window.innerHeight * 0.7;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  renderWidth / renderHeight,
  0.1,
  35000
);

const renderer = new THREE.WebGLRenderer();
renderer.setSize(renderWidth, renderHeight);

const geometryPoints = new THREE.BufferGeometry();

let rawData = [];
let positionPoints = [];
let colors = [];
let particles = new THREE.Points();
let particleMaterial = new THREE.PointsMaterial({
  size: 100,
  vertexColors: true,
  // transparent: true,
  // opacity: 0.75,
});

const controls = new THREE.OrbitControls(camera, renderer.domElement);
const lightAmbient = new THREE.AmbientLight(0xdcdcdc, 0.5);
const lightDirectional = new THREE.DirectionalLight(0xffffff, 0.5);
lightDirectional.position.set(0, 2, 0);

const loader = new THREE.PLYLoader();
let fileName = "";

$(document).ready(function () {
  window.addEventListener("resize", onWindowResize, false);

  fileName = JSON.parse(data);
  loadPLY(fileName);
  // TODO need to update to have more control on where canvas is within the dom
  document.body.appendChild(renderer.domElement);
  // processRawData(rawData[curIndex]);
  animate();
});
// TODO I think the points are so spread out that cant render on the screen
function loadPLY(filename) {
  loader.load(
    "http://localhost:9000/static/ply/" + filename + ".ply",
    function (geometry) {
      console.log(geometry);
      // geometry.computeVertexNormals();

      // var material = new THREE.MeshPhongMaterial({
      //   color: 0xfaf9f6,
      //   wireframe: false,
      // });
      // var mesh = new THREE.Mesh(geometry, material);
      // mesh.position.set(0, 0, 0);

      // mesh.castShadow = true;
      // mesh.receiveShadow = true;
      // scene.add(mesh);
      // scene.add(lightAmbient);
      // scene.add(lightDirectional);

      // create the particles
      processRawData(geometry);
    }
  );
}

function animate() {
  controls.update();
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}

function processRawData(geometry) {
  positionPoints = [];
  colors = [];
  // go through geometry position list size and push color
  for (let i = 0; i < geometry.attributes.position.count; i++) {
    const color = new THREE.Color(0.5, 0.92, 0.1);
    colors.push(color.r, color.g, color.b);
  }
  geometryPoints.setAttribute("position", geometry.attributes.position);
  geometryPoints.setAttribute(
    "color",
    new THREE.Float32BufferAttribute(colors, 3)
  );
  particles = new THREE.Points(geometryPoints, particleMaterial);
  scene.add(particles);
  console.log(particles);

  var sceneBoundingBox = new THREE.Box3().setFromObject(scene);

  // Get the center of the bounding box
  var center = sceneBoundingBox.getCenter(new THREE.Vector3());

  // Get the radius of the bounding box (distance from center to corners)
  var radius = sceneBoundingBox.getSize(new THREE.Vector3()).length() / 2;
  console.log(radius);

  // Calculate the camera distance based on the radius of the bounding box
  var distance = radius / Math.tan(((Math.PI / 180.0) * camera.fov) / 2);

  // Set the camera position and target
  camera.position.set(center.x, center.y, center.z + distance);
  camera.lookAt(center);

  controls.target.set(center.x, center.y, center.z);
  controls.maxDistance = distance * 10;
  console.log(controls.maxDistance);
  controls.update();
}

function onWindowResize() {
  camera.aspect = renderWidth / renderHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(renderWidth, renderHeight);
  animate();
}
