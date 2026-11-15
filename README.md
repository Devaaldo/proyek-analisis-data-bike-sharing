# Proyek Analisis Data: Bike Sharing Dashboard 🚲

Analisis data penyewaan sepeda Capital Bikeshare (Washington D.C., 2011 sampai 2012) untuk menjawab dua pertanyaan bisnis:

1. Berapa persen penurunan rata-rata penyewaan harian saat cuaca berkabut/berawan dan hujan/salju ringan dibanding hari cerah sepanjang 2012?
2. Pada jam berapa penyewaan memuncak di hari kerja dibanding hari libur/akhir pekan 2012, dan berapa porsi pengguna terdaftar di masing-masing jenis hari?

Analisis lengkap ada di `notebook.ipynb`. Hasilnya disajikan dalam dashboard Streamlit di folder `dashboard/`.

## Dashboard Online

https://bdjjf9ei6qsasnz6axc2q9.streamlit.app/

## Struktur Folder

```
submission
├── dashboard
│   ├── dashboard.py
│   └── main_data.csv
├── data
│   ├── day.csv
│   ├── hour.csv
│   └── Readme.txt
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Setup Environment - Anaconda

```
conda create --name main-ds python=3.11
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Menjalankan Dashboard

Dari folder utama proyek (folder yang berisi `requirements.txt`):

```
streamlit run dashboard/dashboard.py
```

Dashboard akan terbuka di `http://localhost:8501`. Gunakan sidebar untuk memilih rentang tanggal dan jenis hari.

## Sumber Data

Fanaee-T, Hadi, and Gama, Joao, "Event labeling combining ensemble detectors and background knowledge", Progress in Artificial Intelligence (2013): pp. 1-15, Springer Berlin Heidelberg, doi:10.1007/s13748-013-0040-3.
