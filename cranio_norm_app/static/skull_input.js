const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.z = 200;

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

const light = new THREE.AmbientLight(0x404040);

// point selection variables
// https://www.youtube.com/watch?v=By9qRmcrTzs&ab_channel=WaelYasmina

// emit a ray from the camera to the user cursor
const rayCaster = new THREE.Raycaster();
// Normalized x, y coordinates of the user's mouse cursor in respect to the window
mouse = new THREE.Vector2();
// coordinate of the user clicked
const intersectionPoint = new THREE.Vector3();
// normalized plane that will provide the direction of the invisible plane
const planeNormal = new THREE.Vector3();
// invisible plane that will contantly update to face the camera as the user moves the cursor
const plane = new THREE.Plane();

$(document).ready(function () {
  // event listener to set normalized coordinates in reference to the windo
  window.addEventListener("mousemove", function (e) {
    mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
    // setting the normalized plane direction based on camera position
    planeNormal.copy(camera.position).normalize();
    // defines the invisble plane
    plane.setFromNormalAndCoplanarPoint(planeNormal, scene.position);
    // emit the ray from camera and mouse
    rayCaster.setFromCamera(mouse, camera);
    // intersecting the ray with a plane and the result copied into intersectionPoint
    rayCaster.ray.intersectPlane(plane, intersectionPoint);
  });

  // onclick create the sphere
  window.addEventListener("click", function (e) {
    if (e.shiftKey) {
      const sphereGeo = new THREE.SphereGeometry(10, 30, 30);
      const sphereMat = new THREE.MeshBasicMaterial({ color: 0xffff00 });
      const sphereMesh = new THREE.Mesh(sphereGeo, sphereMat);
      scene.add(sphereMesh);
      sphereMesh.position.copy(intersectionPoint);
    }
  });
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

// first see what is the array when we hover onto a general point

// function getClicked3DPoint(evt) {
//   evt.preventDefault();

//   mousePosition.x = ((evt.clientX - canvasPosition.left) / canvas.width) * 2 - 1;
//   mousePosition.y = -((evt.clientY - canvasPosition.top) / canvas.height) * 2 + 1;

//   rayCaster.setFromCamera(mousePosition, camera);
//   var intersects = rayCaster.intersectObjects(scene.getObjectByName('MyObj_s').children, true);

//   if (intersects.length > 0)
//       return intersects[0].point;
// };
