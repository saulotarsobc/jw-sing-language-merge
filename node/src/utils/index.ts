import { promisify } from "util";
import unzipper from "unzipper";
import {
  constants,
  access,
  rm,
  createReadStream,
  existsSync,
  mkdirSync,
  copyFile,
  readdirSync,
  copyFileSync,
  mkdir,
} from "fs";
import { join } from "path";

export function createDirectoryIfNotExists(directoryPath: string) {
  try {
    // Tenta criar o diretório com a opção recursive definida como true
    mkdir(directoryPath, { recursive: true }, () => {});
    console.log(`Diretório ${directoryPath} criado com sucesso.`);
  } catch (error) {
    // Se ocorrer um erro ao criar o diretório, ele será tratado aqui
    if (error?.code === "EEXIST") {
      // Se o diretório já existir, apenas exibe uma mensagem de aviso
      console.log(`O diretório ${directoryPath} já existe.`);
    } else {
      // Se ocorrer outro tipo de erro, ele será tratado aqui
      console.error(`Erro ao criar o diretório ${directoryPath}:`, error);
    }
  }
}

/**
 * Deletes the folder with the specified name.
 * If the folder doesn't exist, it logs a message indicating so.
 * If an error occurs during folder deletion, it logs an error message.
 * @param {string} folderName - The name of the folder to delete.
 */
export const deleteFolder = async (folderName: string) => {
  try {
    // Check if the folder exists
    access(folderName, constants.F_OK, () => {});

    // Delete the folder
    rm(folderName, { recursive: true }, () => {});

    // console.log("Pasta deletada com sucesso!");
  } catch (error) {
    console.error("Error deleting the folder:", error);
  }
};

export const unzipBkpFile = async (
  zipFilePath: string,
  destinationPath: string
) => {
  if (!existsSync(destinationPath)) {
    mkdirSync(destinationPath, { recursive: true });
  }

  const pipeline = promisify(require("stream").pipeline);

  await pipeline(
    createReadStream(zipFilePath),
    unzipper.Extract({ path: destinationPath })
  );

  // console.log("Arquivo .zip descompactado com sucesso.");
};

export async function copyFiles(sourceDir: string, destinationDir: string) {
  try {
    // Lista os arquivos no diretório de origem
    const files = await readdirSync(sourceDir);

    // Itera sobre cada arquivo e os copia para o diretório de destino
    for (const file of files) {
      const sourceFile = join(sourceDir, file);
      const destinationFile = join(destinationDir, file);

      // Copia o arquivo para o diretório de destino
      await copyFileSync(sourceFile, destinationFile);

      console.log(`Arquivo ${file} copiado para ${destinationDir}`);
    }

    console.log("Todos os arquivos foram copiados com sucesso.");
  } catch (error) {
    console.error("Erro ao copiar arquivos:", error);
  }
}
