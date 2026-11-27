// v8 3D shot kit: physically lit devices and screens for the FLMLNK film.
// Every shot is a pure function of time: shot.render(tLocal, dur) draws one frame.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const W = 1080, H = 1920;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const inv = (a, b, x) => clamp((x - a) / (b - a));
const sine = t => -(Math.cos(Math.PI * clamp(t)) - 1) / 2;          // ease in-out
const out3 = t => 1 - Math.pow(1 - clamp(t), 3);                      // ease out
const spring = t => { t = Math.max(0, t); const k = 9, w = 8; return 1 - Math.exp(-k * t) * (Math.cos(w * t) + (k / w) * Math.sin(w * t)); };
const lerp = THREE.MathUtils.lerp;

export const canvas = document.createElement('canvas');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H); renderer.setPixelRatio(1);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const ENV = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;

// ---------- assets ----------
const loadImg = src => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = src; });
const CAT = ['engine-hearts', 'night-desk', 'orbit-nine', 'red-ledger', 'kinfolk-road', 'hollow-acre', 'cinder-line', 'the-glass-orchard',
  'saltwater-kings', 'iron-hollow', 'paper-crowns', 'dust-diamonds', 'mile-marker-9', 'twelve-rounds-deep', 'snowbound-at-maple-inn', 'sweet-revenge-bakery'];
const IMG = {}, TEX = {}, DIM = {};
function canvasTex(c) { const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; }
function rr(g, x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }
function imgTex(im, { gray = false, crop = null, w = 1280, h = 720, radius = 28 } = {}) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d');
  g.save(); rr(g, 0, 0, w, h, radius); g.clip();
  g.filter = gray ? 'grayscale(1) brightness(0.38)' : 'none';
  if (crop) g.drawImage(im, crop[0], crop[1], crop[2], crop[3], 0, 0, w, h); else g.drawImage(im, 0, 0, w, h);
  g.restore(); return canvasTex(c);
}
export async function loadAssets() {
  await document.fonts.load('500 40px "DM Sans"'); await document.fonts.load('400 30px "DM Sans"'); await document.fonts.load('italic 40px "Instrument Serif"');
  await Promise.all(CAT.map(async n => { IMG[n] = await loadImg('assets/cat/' + n + '.jpg'); }));
  IMG.mark = await loadImg('assets/mark_base.png'); IMG.wedge = await loadImg('assets/mark_wedge.png');
  CAT.forEach(n => { TEX[n] = imgTex(IMG[n]); DIM[n] = imgTex(IMG[n], { gray: true }); });
  for (const s of SHOTS3D) s.build && s.build();
}

// ---------- shared studio ----------
function studio({ floor = true, fogNear = 10, fogFar = 26, key = 2.6, rim = 1.6 } = {}) {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#0B0D10');
  scene.fog = new THREE.Fog('#0B0D10', fogNear, fogFar);
  scene.environment = ENV; scene.environmentIntensity = 0.35;
  const k = new THREE.DirectionalLight('#ffd8b0', key); k.position.set(-5, 8, 6); k.castShadow = true;
  k.shadow.mapSize.set(2048, 2048); Object.assign(k.shadow.camera, { left: -8, right: 8, top: 8, bottom: -8 }); k.shadow.radius = 7; k.shadow.bias = -0.0004;
  scene.add(k);
  const r = new THREE.DirectionalLight('#b9c8ff', rim); r.position.set(6, 4, -6); scene.add(r);
  scene.add(new THREE.HemisphereLight('#3a3530', '#050506', 0.45));
  if (floor) {
    const f = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), new THREE.MeshStandardMaterial({ color: '#111216', roughness: 0.92 }));
    f.rotation.x = -Math.PI / 2; f.receiveShadow = true; scene.add(f);
  }
  return scene;
}
function cam(fov = 26) { return new THREE.PerspectiveCamera(fov, W / H, 0.1, 120); }
function post(scene, camera, aperture = 0.002, maxblur = 0.01) {
  const c = new EffectComposer(renderer); c.setSize(W, H);
  c.addPass(new RenderPass(scene, camera));
  const b = new BokehPass(scene, camera, { focus: 10, aperture, maxblur }); c.addPass(b);
  c.addPass(new OutputPass());
  return { composer: c, bokeh: b };
}
const METAL = () => new THREE.MeshPhysicalMaterial({ color: '#2a2b2f', metalness: 1, roughness: 0.3, clearcoat: 0.3, clearcoatRoughness: 0.4 });
function glassLayer(w, h, z) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshPhysicalMaterial({ color: '#000', roughness: 0.04, transparent: true, opacity: 0.16, clearcoat: 1, envMapIntensity: 2.2 }));
  m.position.z = z; return m;
}
// a thin glass screen slab showing a texture (title tiles, TV)
function slab(tex, w = 1.6, aspect = 9 / 16, depth = 0.045) {
  const h = w * aspect, g = new THREE.Group();
  const body = new THREE.Mesh(new RoundedBoxGeometry(w + 0.05, h + 0.05, depth, 4, 0.05), METAL()); body.castShadow = true; g.add(body);
  const scr = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false, transparent: true }));
  scr.position.z = depth / 2 + 0.001; g.add(scr); g.add(glassLayer(w, h, depth / 2 + 0.003));
  g.userData.screen = scr; return g;
}
// a device (phone / tablet) with a UI canvas texture
function device(tex, w, h, depth, radius) {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new RoundedBoxGeometry(w + 0.12, h + 0.12, depth, 6, radius), METAL()); body.castShadow = true; g.add(body);
  const scr = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false }));
  scr.position.z = depth / 2 + 0.001; g.add(scr); g.add(glassLayer(w + 0.08, h + 0.08, depth / 2 + 0.004));
  g.userData.screen = scr; return g;
}
function focusOn(bokeh, camera, obj, local = new THREE.Vector3()) { const p = local.clone(); obj.localToWorld(p); bokeh.uniforms.focus.value = camera.position.distanceTo(p); }
function setOpacity(group, o) { group.traverse(m => { if (m.material) { m.material.transparent = true; m.material.opacity = (m.userData.baseOpacity ??= m.material.opacity) * o; } }); group.visible = o > 0.001; }

// ---------- UI canvases ----------
function catalogUI(litIndex = 4) {
  const SW = 1200, SH = 1700, c = document.createElement('canvas'); c.width = SW; c.height = SH; const g = c.getContext('2d');
  g.fillStyle = '#0E0F12'; g.fillRect(0, 0, SW, SH);
  const mw = 190, mh = mw * 279 / 970; g.drawImage(IMG.mark, 70, 78, mw, mh); g.drawImage(IMG.wedge, 70, 78, mw, mh);
  g.fillStyle = 'rgba(243,238,229,.55)'; g.font = '400 30px "DM Sans"'; g.fillText('Your catalog', 70, 200);
  g.fillStyle = '#F3EEE5'; g.font = '500 54px "DM Sans"'; g.fillText('Which titles to back', 70, 262);
  const names = ['orbit-nine', 'the-glass-orchard', 'mile-marker-9', 'night-desk', 'cinder-line', 'dust-diamonds', 'engine-hearts', 'hollow-acre'];
  const gx = 70, gy = 320, gap = 28, tw = (SW - 2 * gx - gap) / 2, th = tw * 9 / 16, rects = [];
  names.forEach((n, i) => {
    const x = gx + (i % 2) * (tw + gap), y = gy + Math.floor(i / 2) * (th + gap + 54); rects.push([x, y, tw, th]);
    g.save(); rr(g, x, y, tw, th, 18); g.clip(); g.filter = 'grayscale(1) brightness(0.42)'; g.drawImage(IMG[n], x, y, tw, th); g.restore();
    g.font = '400 26px "DM Sans"'; g.fillStyle = 'rgba(243,238,229,.35)'; g.fillText('Watching', x, y + th + 38);
  });
  // the lit tile is drawn separately so it can light up over time
  const lit = document.createElement('canvas'); lit.width = SW; lit.height = SH; const l = lit.getContext('2d');
  const [x, y, tw2, th2] = rects[litIndex];
  l.save(); rr(l, x, y, tw2, th2, 18); l.clip(); l.drawImage(IMG[names[litIndex]], x, y, tw2, th2); l.restore();
  l.lineWidth = 7; l.strokeStyle = '#D5111C'; rr(l, x + 3.5, y + 3.5, tw2 - 7, th2 - 7, 16); l.stroke();
  l.fillStyle = '#0E0F12'; l.fillRect(x, y + th2 + 8, 220, 44);
  l.fillStyle = '#D5111C'; l.beginPath(); l.arc(x + 12, y + th2 + 29, 9, 0, 7); l.fill();
  l.font = '500 26px "DM Sans"'; l.fillStyle = '#F3EEE5'; l.fillText('Backed', x + 34, y + th2 + 38);
  return { base: canvasTex(c), lit: canvasTex(lit), aspect: SH / SW, litRect: rects[litIndex], SW, SH };
}
function phoneUI() {
  const SW = 900, SH = 1950, c = document.createElement('canvas'); c.width = SW; c.height = SH; const g = c.getContext('2d');
  g.fillStyle = '#000'; g.fillRect(0, 0, SW, SH);
  const im = IMG['engine-hearts']; const sw = im.height * SW / (SH * 0.74);
  g.drawImage(im, im.width * 0.62 - sw / 2, 0, sw, im.height, 0, 0, SW, SH * 0.74);
  const grad = g.createLinearGradient(0, SH * 0.6, 0, SH * 0.74); grad.addColorStop(0, 'rgba(0,0,0,0)'); grad.addColorStop(1, '#000'); g.fillStyle = grad; g.fillRect(0, SH * 0.6, SW, SH * 0.14);
  g.fillStyle = '#D5111C'; g.beginPath(); g.arc(80, 150, 26, 0, 7); g.fill();
  g.fillStyle = '#F3EEE5'; g.font = '500 40px "DM Sans"'; g.fillText('flmlnk', 124, 164);
  g.font = '500 54px "DM Sans"'; g.fillText('Some stories stay with you.', 60, SH * 0.8);
  g.font = '400 36px "DM Sans"'; g.fillStyle = '#A3A3A3'; g.fillText('There’s a whole film behind this moment.', 60, SH * 0.8 + 64);
  g.fillStyle = '#D5111C'; g.font = '500 40px "DM Sans"'; g.fillText('♥  4,812', 60, SH * 0.8 + 160);
  return { tex: canvasTex(c), aspect: SH / SW };
}
function commentCard(initials, text) {
  const w = 1100, h = 230, c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d');
  g.fillStyle = '#F4F0E9'; rr(g, 0, 0, w, h, 56); g.fill();
  g.fillStyle = '#26241F'; g.beginPath(); g.arc(110, h / 2, 62, 0, 7); g.fill();
  g.fillStyle = '#F4F0E9'; g.font = '500 44px "DM Sans"'; g.textAlign = 'center'; g.fillText(initials, 110, h / 2 + 15);
  g.textAlign = 'left'; g.fillStyle = '#81796E'; g.font = '400 34px "DM Sans"'; g.fillText('New viewer', 210, 92);
  g.fillStyle = '#26241F'; g.font = '500 52px "DM Sans"'; g.fillText(text, 210, 160);
  g.fillStyle = '#D5111C'; g.font = '500 50px "DM Sans"'; g.fillText('♥', w - 90, h / 2 + 16);
  const m = new THREE.Mesh(new THREE.PlaneGeometry(2.2, 2.2 * h / w), new THREE.MeshBasicMaterial({ map: canvasTex(c), transparent: true, toneMapped: false }));
  return m;
}
function bubble(text) {
  const w = 1400, h = 380, c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d');
  g.fillStyle = '#D5111C'; g.beginPath(); g.roundRect(0, 0, w, h - 40, [70, 70, 70, 16]); g.fill();
  g.fillStyle = '#fff'; g.font = '500 76px "DM Sans"';
  const words = text.split(' '); let line = '', y = 135; for (const wd of words) { if (g.measureText(line + wd).width > w - 140) { g.fillText(line, 70, y); line = ''; y += 96; } line += wd + ' '; } g.fillText(line, 70, y);
  return new THREE.Mesh(new THREE.PlaneGeometry(3.0, 3.0 * h / w), new THREE.MeshBasicMaterial({ map: canvasTex(c), transparent: true, toneMapped: false }));
}

// ---------- shots ----------
function shot(o) { return o; }

// 1. Poster stack: five glass title slabs rise and fan in depth, camera low and close
const Stack = shot({
  build() {
    this.scene = studio(); this.camera = cam(28); Object.assign(this, post(this.scene, this.camera, 0.0025, 0.012));
    this.slabs = ['cinder-line', 'night-desk', 'engine-hearts', 'orbit-nine', 'kinfolk-road'].map((n, i) => { const s = slab(TEX[n], 2.6); this.scene.add(s); return s; });
  },
  render(t) {
    const k = sine(inv(0, 1.45, t));
    this.slabs.forEach((s, i) => {
      const o = i - 2, a = out3(inv(i * 0.06, 0.9 + i * 0.06, t));
      s.position.set(o * 0.18, 2.2 + o * lerp(0.2, 1.62, a), -Math.abs(o) * lerp(0.1, 0.55, a));
      s.rotation.set(lerp(-0.9, -0.12, a), o * -0.05, o * 0.04);
      setOpacity(s, inv(i * 0.06, i * 0.06 + 0.18, t));
    });
    this.camera.position.set(lerp(-1.6, -0.9, k), lerp(2.6, 2.4, k), lerp(11.5, 10.6, k)); this.camera.lookAt(0, 2.2, 0);
    focusOn(this.bokeh, this.camera, this.slabs[2]); this.composer.render();
  },
});

// 2. Depth wall: a field of dim title screens; the camera drifts through, three light up
const Wall = shot({
  build() {
    this.scene = studio({ floor: false, fogNear: 8, fogFar: 22 }); this.camera = cam(30); Object.assign(this, post(this.scene, this.camera, 0.003, 0.014));
    this.tiles = []; let n = 0;
    for (let r = 0; r < 9; r++) for (let c = 0; c < 4; c++) {
      const name = CAT[(n * 7 + r) % CAT.length]; const s = slab(DIM[name], 1.5); const z = -((r * 4 + c) % 5) * 0.9;
      s.position.set((c - 1.5) * 1.75 + (r % 2) * 0.4, (r - 4) * 1.05, z); s.rotation.y = -0.25; this.scene.add(s);
      s.userData.name = name; s.userData.lit = [13, 22, 26].includes(n); this.tiles.push(s); n++;
    }
  },
  render(t, dur) {
    const k = t / dur;
    this.tiles.forEach(s => { if (s.userData.lit) s.userData.screen.material.map = t > 0.35 ? TEX[s.userData.name] : DIM[s.userData.name]; });
    this.camera.position.set(lerp(-0.6, 0.4, k), lerp(0.6, -0.5, k), lerp(9.5, 8.4, k)); this.camera.lookAt(lerp(0, 0.6, k), lerp(0.3, -0.6, k), -1.5);
    focusOn(this.bokeh, this.camera, this.tiles[22]); this.composer.render();
  },
});

// 3. Phone: a post, viewer comments float in beside it
const Phone = shot({
  build() {
    this.scene = studio(); this.camera = cam(26); Object.assign(this, post(this.scene, this.camera, 0.0022, 0.01));
    const ui = phoneUI(); const w = 2.0; this.phone = device(ui.tex, w, w * ui.aspect, 0.16, 0.26);
    this.phone.position.set(-0.5, w * ui.aspect / 2 + 0.12, 0); this.phone.rotation.set(-0.08, 0.32, 0); this.scene.add(this.phone);
    this.cards = [['AR', 'Where can I watch this?'], ['TJ', 'How did I miss this film?'], ['MP', 'That’s tonight’s movie sorted.']].map(([a, q]) => { const m = commentCard(a, q); m.scale.setScalar(0.86); this.scene.add(m); return m; });
  },
  render(t) {
    const k = sine(inv(0, 1.9, t));
    this.cards.forEach((m, i) => {
      const st = 0.35 + i * 0.32, a = spring((t - st) * 1.5);
      m.position.set(lerp(2.0, 0.55, clamp(a, 0, 1.05)), 3.4 - i * 0.55, 0.7 + i * 0.1); m.rotation.y = 0.22;
      m.material.opacity = inv(st, st + 0.18, t); m.visible = t > st;
    });
    this.camera.position.set(lerp(1.2, 0.7, k), lerp(3.0, 2.8, k), lerp(13.0, 12.0, k)); this.camera.lookAt(0.25, 2.5, 0);
    focusOn(this.bokeh, this.camera, this.phone); this.composer.render();
  },
});

// 4. Catalog tablet + the red question; one title lights up and is backed
const Tablet = shot({
  build() {
    this.scene = studio(); this.camera = cam(26); Object.assign(this, post(this.scene, this.camera, 0.0022, 0.01));
    const ui = catalogUI(); this.ui = ui; const w = 3.0;
    this.tab = device(ui.base, w, w * ui.aspect, 0.11, 0.16);
    const lit = new THREE.Mesh(new THREE.PlaneGeometry(w, w * ui.aspect), new THREE.MeshBasicMaterial({ map: ui.lit, transparent: true, toneMapped: false, opacity: 0 }));
    lit.position.z = 0.0565; this.tab.add(lit); this.lit = lit;
    const [rx, ry, rw, rh] = ui.litRect, th = w * ui.aspect;
    this.tile = new THREE.Vector3(((rx + rw / 2) / ui.SW - 0.5) * w, (0.5 - (ry + rh / 2) / ui.SH) * th, 0.06);
    this.tab.rotation.set(-0.26, 0.3, 0); this.tab.position.set(0, w * ui.aspect / 2 * Math.cos(0.26) + 0.02, -0.25); this.scene.add(this.tab);
    this.q = bubble('Which titles in our catalog are worth another dollar?'); this.scene.add(this.q);
  },
  render(t) {
    const k = sine(inv(0, 1.9, t));
    const b = spring(t * 1.5); this.q.position.set(-0.3, lerp(4.75, 4.55, clamp(b, 0, 1.05)), 1.2); this.q.scale.setScalar(0.85 + 0.15 * clamp(b, 0, 1.05));
    this.q.material.opacity = inv(0, 0.2, t);
    this.lit.material.opacity = inv(0.95, 1.25, t);
    this.camera.position.set(Math.sin(lerp(-0.34, -0.18, k)) * lerp(14.6, 13.6, k), lerp(3.6, 3.3, k), Math.cos(lerp(-0.34, -0.18, k)) * lerp(14.6, 13.6, k));
    this.camera.lookAt(0.05, 2.55, 0);
    focusOn(this.bokeh, this.camera, this.tab, this.tile); this.composer.render();
  },
});

// 5. Tablet macro: push in on the backed title (replaces the AI hand)
const Macro = shot({
  build() { this.src = Tablet; this.camera = cam(22); Object.assign(this, post(Tablet.scene, this.camera, 0.006, 0.02)); },
  render(t, dur) {
    const k = sine(t / dur); Tablet.lit.material.opacity = 1; Tablet.q.material.opacity = 0;
    const p = Tablet.tile.clone(); Tablet.tab.localToWorld(p);
    this.camera.position.set(p.x + lerp(1.3, 0.8, k), p.y + lerp(0.9, 0.6, k), p.z + lerp(4.6, 3.6, k)); this.camera.lookAt(p.x, p.y - 0.05, p.z);
    this.bokeh.uniforms.focus.value = this.camera.position.distanceTo(p); this.composer.render();
  },
});

// 6. Handoff: the phone glides toward a large screen where the full film plays
const Handoff = shot({
  build() {
    this.scene = studio(); this.camera = cam(28); Object.assign(this, post(this.scene, this.camera, 0.0022, 0.012));
    this.tv = slab(TEX['engine-hearts'], 5.6, 9 / 16, 0.12); this.tv.position.set(0.6, 3.4, -3.2); this.scene.add(this.tv);
    const ui = phoneUI(); this.phone = device(ui.tex, 1.3, 1.3 * ui.aspect, 0.12, 0.2); this.scene.add(this.phone);
  },
  render(t, dur) {
    const k = sine(t / dur), m = sine(inv(0.1, 0.95, t / dur));
    this.phone.position.set(lerp(-1.4, 0.2, m), lerp(2.0, 3.1, m), lerp(2.6, -1.2, m)); this.phone.rotation.set(-0.05, lerp(0.45, 0.05, m), lerp(-0.08, 0, m));
    setOpacity(this.phone, 1 - inv(0.7, 0.98, t / dur));
    this.camera.position.set(lerp(-0.6, 0.2, k), lerp(2.6, 3.0, k), lerp(11.6, 10.4, k)); this.camera.lookAt(0.3, 3.0, -1.5);
    focusOn(this.bokeh, this.camera, m > 0.6 ? this.tv : this.phone); this.composer.render();
  },
});

// 7. Red wedge macro: the logo's red wedge as a lacquered object, light sweeping across
const Wedge = shot({
  build() {
    this.scene = studio({ floor: false, key: 1.4, rim: 2.4 }); this.camera = cam(24); Object.assign(this, post(this.scene, this.camera, 0.004, 0.02));
    const s = new THREE.Shape(); s.moveTo(1.6, 0); s.lineTo(1.6, 1.4); s.lineTo(0, 0); s.lineTo(1.6, 0);
    const geo = new THREE.ExtrudeGeometry(s, { depth: 0.45, bevelEnabled: true, bevelThickness: 0.06, bevelSize: 0.05, bevelSegments: 8, curveSegments: 12 }); geo.center();
    this.w = new THREE.Mesh(geo, new THREE.MeshPhysicalMaterial({ color: '#D5111C', roughness: 0.18, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.05, envMapIntensity: 1.4 }));
    this.scene.add(this.w);
    this.sweep = new THREE.SpotLight('#ffffff', 60, 12, 0.35, 0.6); this.scene.add(this.sweep); this.scene.add(this.sweep.target);
  },
  render(t, dur) {
    const k = sine(t / dur);
    this.w.rotation.set(lerp(-0.35, -0.2, k), lerp(-0.7, -0.25, k), lerp(0.1, 0.02, k));
    this.sweep.position.set(lerp(-4, 4, k), 3, 4); this.sweep.target.position.set(0, 0, 0);
    this.camera.position.set(0.1, 0.1, lerp(7.2, 6.2, k)); this.camera.lookAt(0.05, 0, 0);
    this.bokeh.uniforms.focus.value = this.camera.position.distanceTo(new THREE.Vector3(0, 0, 0.3)); this.composer.render();
  },
});

// 8. Carousel: title screens on a curved rail turn past camera and land on the hero title
const Carousel = shot({
  build() {
    this.scene = studio(); this.camera = cam(30); Object.assign(this, post(this.scene, this.camera, 0.0025, 0.012));
    this.rail = new THREE.Group(); this.scene.add(this.rail); this.rail.position.z = -6.5; this.R = 6.5; this.step = 0.42;
    ['red-ledger', 'the-glass-orchard', 'orbit-nine', 'saltwater-kings', 'kinfolk-road', 'engine-hearts'].forEach((n, i) => {
      const s = slab(TEX[n], 2.8); const a = i * this.step; s.position.set(Math.sin(a) * this.R, 2.6, Math.cos(a) * this.R); s.rotation.y = a; this.rail.add(s);
    });
  },
  render(t, dur) {
    const n = 5, k = sine(inv(0, dur * 0.95, t));
    this.rail.rotation.y = -lerp(n - 3, n, k) * this.step;
    this.camera.position.set(0, 3.0, 12.4); this.camera.lookAt(0, 2.6, 0);
    this.bokeh.uniforms.focus.value = 12.4; this.composer.render();
  },
});

export const SHOTS3D = [Stack, Wall, Phone, Tablet, Macro, Handoff, Wedge, Carousel];
export const S3 = { Stack, Wall, Phone, Tablet, Macro, Handoff, Wedge, Carousel };
