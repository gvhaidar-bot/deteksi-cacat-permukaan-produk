const zonaJatuh = document.getElementById("zonaJatuh");
const masukanBerkas = document.getElementById("masukanBerkas");
const gambarPratinjau = document.getElementById("gambarPratinjau");
const keteranganPratinjau = document.getElementById("keteranganPratinjau");
const pilihanSensitivitas = document.getElementById("pilihanSensitivitas");
const masukanLuasMinimum = document.getElementById("masukanLuasMinimum");
const nilaiLuasMinimum = document.getElementById("nilaiLuasMinimum");
const tombolProses = document.getElementById("tombolProses");
const statusProses = document.getElementById("statusProses");
const galeriContoh = document.getElementById("galeriContoh");
const kotakVerdict = document.getElementById("kotakVerdict");
const teksVerdict = document.getElementById("teksVerdict");
const teksKeparahan = document.getElementById("teksKeparahan");
const galeriTahapan = document.getElementById("galeriTahapan");
const badanTabelCacat = document.getElementById("badanTabelCacat");

const LABEL_TAHAPAN = [
  ["asli", "1. Citra Asli", "Citra produk yang diunggah."],
  ["grayscale", "2. Grayscale", "Konversi ke citra keabuan 1 kanal."],
  ["blur", "3. Gaussian Blur", "Filter 5×5 untuk menekan noise butiran permukaan."],
  ["blackhat", "4. Black-Hat", "Morfologi closing − citra: menonjolkan cacat yang lebih gelap dari sekitarnya."],
  ["tophat", "5. Top-Hat", "Morfologi citra − opening: menonjolkan cacat yang lebih terang dari sekitarnya."],
  ["peta_anomali", "6. Peta Anomali", "Gabungan black-hat + top-hat."],
  ["masker", "7. Masker Segmentasi", "Threshold Otsu + opening/closing morfologi."],
  ["tepi_canny", "8. Tepi Canny", "Deteksi tepi untuk menangkap goresan dan retakan tipis."],
  ["hasil", "9. Hasil Deteksi", "Kontur merah dan kotak pembatas oranye pada setiap cacat."],
];

let berkasTerpilih = null;
let contohTerpilih = null;

function segarkanTombol() {
  tombolProses.disabled = !berkasTerpilih && !contohTerpilih;
}

function tampilkanPratinjau(url, keterangan) {
  gambarPratinjau.src = url;
  gambarPratinjau.hidden = false;
  keteranganPratinjau.textContent = keterangan;
}

function pilihBerkas(berkas) {
  if (!berkas) return;
  berkasTerpilih = berkas;
  contohTerpilih = null;
  document.querySelectorAll(".contoh-item").forEach((el) => el.classList.remove("aktif"));
  tampilkanPratinjau(URL.createObjectURL(berkas), "Berkas: " + berkas.name);
  segarkanTombol();
}

zonaJatuh.addEventListener("dragover", (e) => {
  e.preventDefault();
  zonaJatuh.classList.add("menyeret");
});
zonaJatuh.addEventListener("dragleave", () => zonaJatuh.classList.remove("menyeret"));
zonaJatuh.addEventListener("drop", (e) => {
  e.preventDefault();
  zonaJatuh.classList.remove("menyeret");
  if (e.dataTransfer.files.length > 0) pilihBerkas(e.dataTransfer.files[0]);
});
masukanBerkas.addEventListener("change", () => pilihBerkas(masukanBerkas.files[0]));

masukanLuasMinimum.addEventListener("input", () => {
  const nilai = parseInt(masukanLuasMinimum.value, 10);
  nilaiLuasMinimum.textContent = nilai === 0 ? "bawaan preset" : nilai + " piksel";
});

function luasMinimumKirim() {
  const nilai = parseInt(masukanLuasMinimum.value, 10);
  return nilai === 0 ? "" : String(nilai);
}

function aturStatus(teks, galat) {
  statusProses.textContent = teks;
  statusProses.classList.toggle("galat", Boolean(galat));
}

function tampilkanHasil(data) {
  const r = data.ringkasan;
  kotakVerdict.className = "kotak-verdict " + (r.verdict === "CACAT" ? "cacat" : "lulus");
  teksVerdict.textContent = r.verdict === "CACAT"
    ? "HASIL: CACAT — produk ditolak"
    : "HASIL: LULUS — tidak ditemukan cacat signifikan";
  if (r.verdict === "CACAT") {
    teksKeparahan.hidden = false;
    teksKeparahan.textContent = "Keparahan: " + r.keparahan;
  } else {
    teksKeparahan.hidden = true;
  }
  document.getElementById("metrikJumlah").textContent = r.jumlah_cacat;
  document.getElementById("metrikLuas").textContent = r.luas_cacat_persen + " %";
  document.getElementById("metrikAmbang").textContent = r.ambang_terpakai + " (Otsu " + r.ambang_otsu + ")";
  document.getElementById("metrikUkuran").textContent = r.ukuran.lebar + " × " + r.ukuran.tinggi + " px";
  document.getElementById("metrikRata").textContent = r.rata_rata_intensitas;
  document.getElementById("metrikEntropi").textContent = r.entropi;

  galeriTahapan.innerHTML = "";
  LABEL_TAHAPAN.forEach(([kunci, judul, penjelasan]) => {
    if (!data.tahapan[kunci]) return;
    const figur = document.createElement("figure");
    figur.className = "tahap";
    const img = document.createElement("img");
    img.src = data.tahapan[kunci];
    img.alt = judul;
    const kapsyen = document.createElement("figcaption");
    kapsyen.textContent = judul;
    const par = document.createElement("p");
    par.textContent = penjelasan;
    figur.append(img, kapsyen, par);
    galeriTahapan.appendChild(figur);
  });

  badanTabelCacat.innerHTML = "";
  if (r.daftar_cacat.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 5;
    td.className = "sel-kosong";
    td.textContent = "Tidak ada kontur cacat yang memenuhi syarat luas minimum.";
    tr.appendChild(td);
    badanTabelCacat.appendChild(tr);
    return;
  }
  r.daftar_cacat.forEach((cacat) => {
    const tr = document.createElement("tr");
    const nilai = [
      cacat.nomor,
      cacat.jenis_dugaan,
      cacat.luas_piksel,
      cacat.luas_persen,
      cacat.kotak.x + ", " + cacat.kotak.y + ", " + cacat.kotak.lebar + " × " + cacat.kotak.tinggi,
    ];
    nilai.forEach((isi) => {
      const td = document.createElement("td");
      td.textContent = isi;
      tr.appendChild(td);
    });
    badanTabelCacat.appendChild(tr);
  });
}

async function proses() {
  aturStatus("Memproses citra...", false);
  tombolProses.disabled = true;
  try {
    let respons;
    if (berkasTerpilih) {
      const formulir = new FormData();
      formulir.append("gambar", berkasTerpilih);
      formulir.append("sensitivitas", pilihanSensitivitas.value);
      formulir.append("luas_minimum", luasMinimumKirim());
      respons = await fetch("/api/deteksi", { method: "POST", body: formulir });
    } else if (contohTerpilih) {
      respons = await fetch("/api/deteksi-contoh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          kelas: contohTerpilih.kelas,
          nama: contohTerpilih.nama,
          sensitivitas: pilihanSensitivitas.value,
          luas_minimum: luasMinimumKirim(),
        }),
      });
    } else {
      aturStatus("Pilih citra atau contoh dataset dulu.", true);
      return;
    }
    const data = await respons.json();
    if (!respons.ok) {
      aturStatus(data.galat || "Terjadi kesalahan pada server.", true);
      return;
    }
    tampilkanHasil(data);
    aturStatus("Selesai. Hasil ditampilkan di panel kanan.", false);
  } catch (err) {
    aturStatus("Tidak dapat terhubung ke server. Pastikan backend Flask berjalan.", true);
  } finally {
    segarkanTombol();
  }
}

tombolProses.addEventListener("click", proses);

async function muatContoh() {
  try {
    const respons = await fetch("/api/contoh");
    const data = await respons.json();
    galeriContoh.innerHTML = "";
    data.contoh.forEach((contoh) => {
      const tombol = document.createElement("button");
      tombol.type = "button";
      tombol.className = "contoh-item";
      const img = document.createElement("img");
      img.src = contoh.url;
      img.alt = contoh.kelas + " " + contoh.nama;
      img.loading = "lazy";
      const span = document.createElement("span");
      span.textContent = contoh.kelas;
      tombol.append(img, span);
      tombol.addEventListener("click", () => {
        document.querySelectorAll(".contoh-item").forEach((el) => el.classList.remove("aktif"));
        tombol.classList.add("aktif");
        berkasTerpilih = null;
        masukanBerkas.value = "";
        contohTerpilih = contoh;
        tampilkanPratinjau(contoh.url, "Contoh dataset: " + contoh.kelas + "/" + contoh.nama);
        segarkanTombol();
        proses();
      });
      galeriContoh.appendChild(tombol);
    });
  } catch (err) {
    galeriContoh.innerHTML = "<p class='petunjuk'>Galeri contoh gagal dimuat.</p>";
  }
}

muatContoh();
