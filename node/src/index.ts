import { deleteFolder, unzipBkpFile, copyFiles, createFolder } from "./utils";

const JWFILE1 = "bkp1.jwlibrary";
const JWFILE2 = "bkp2.jwlibrary";
const FINALFILENAME = "Merged_Backup.jwlibrary";
const HASH = "<=hash>=";
const FOLDERS = ["data-1", "data-2", "data-3"];

// main
async function main() {
  // console.log("> Criando pastas");
  // FOLDERS.forEach((folderName) => {
  //   createFolder(folderName);
  // });

  console.log(">> Descopactando bkp 1 e compiando seus arquivos para data-1");
  await unzipBkpFile(JWFILE1, "data-1");

  console.log(">> Descopactando bkp 2 e compiando seus arquivos para data-2");
  await unzipBkpFile(JWFILE2, "data-2");

  console.log(">> Copiando todos os arquivos de /data 1 e 2 para 3");
  copyFiles("./data-1", "data-3");

  // console.log(">> Deletandto pastas...");
  // FOLDERS.forEach((folderName) => {
  //   deleteFolder(folderName);
  // });
}

main();
