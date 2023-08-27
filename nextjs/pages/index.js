import Image from "next/image";
import { useState, useRef } from "react";

export default function Home() {
  const [images, setImages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const audioRef = useRef(null);
  const [fileName, setFileName] = useState("");

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Play the song while generating images
    const url = URL.createObjectURL(file);
    setFileName(file.fileName)
    audioRef.current.src = url;
    audioRef.current.play();

    setUploading(true);

    const formData = new FormData();
    formData.append("song", file);

    try {
      const response = await fetch("http://127.0.0.1:5000/get_images", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const data = await response.json();
      setImages(data);
    } catch (error) {
      console.error(error);
    } finally {
      setUploading(false);
    }
  };

  const resetProcess = () => {
    setImages([]);
  };

  const downloadImage = (src) => {
    window.open(src, "_blank")
  }

  return (
    <main className="font-roboto flex min-h-screen flex-col items-center justify-center bg-gray-100 text-gray-900">
      <h1 className="mb-8 text-4xl font-bold">Song Art Generator</h1>
      {fileName ? (<h2 className="my-8 text-2xl">{fileName}</h2>) : (<></>)} 
      {images.length ? (
        <>
          <div className="grid grid-cols-2 gap-4">
            {images.map((src, index) => (
              <div key={index} className="h-64 w-64">
                <div className="fixed w-64 h-64 bg-black bg-opacity-50  opacity-0 hover:opacity-100 flex items-center justify-center cursor-pointer transition duration-500" onClick={() => {downloadImage(src)}}>
                  <p className="text-white opacity-100">Download Image</p>
                </div>
                <Image
                  src={src}
                  alt="Album Cover"
                  className="h-full w-full object-cover"
                  width={256}
                  height={256}
                />
              </div>
            ))}
          </div>
          <button
            onClick={resetProcess}
            className="mt-8 rounded bg-gray-800 px-6 py-3 text-lg font-medium tracking-wide text-white transition duration-300 hover:bg-gray-700"
          >
            Upload another song
          </button>
        </>
      ) : (
        <div className="flex items-center justify-center">
          <label
            htmlFor="upload-button"
            className={`${
              uploading ? "cursor-not-allowed opacity-50" : "hover:bg-gray-700"
            } cursor-pointer rounded bg-gray-800 px-6 py-3 text-lg font-medium tracking-wide text-white transition duration-300`}
          >
            {uploading ? "Generating images..." : "Upload Song (mp3)"}
            <input
              type="file"
              id="upload-button"
              className="hidden"
              accept="audio/*"
              onChange={handleFileUpload}
              disabled={uploading}
            />
          </label>
        </div>
      )}
      <audio ref={audioRef} />
    </main>
  );
}
