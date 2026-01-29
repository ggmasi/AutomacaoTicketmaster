import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import requests
import winsound
import os

# --- CONFIGURAÇÕES ---
TOKEN_TELEGRAM = "8309215528:AAEXv8N0cSaAP0cao2uFT0s5j0CygDyiSRM"
CHAT_ID = "7758229260"
URLS = [
    "https://www.ticketmaster.com.br/event/bad-bunny-venda-geral-21-02",
    "https://www.ticketmaster.com.br/event/bad-bunny-venda-geral"
]

def tocar_melodia_agradavel():
    notas = [659, 783, 1046]
    for n in notas:
        winsound.Beep(n, 350)
        time.sleep(0.05)

def enviar_telegram(mensagem, driver):
    url_photo = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendPhoto"
    foto_path = "venda_bunny.png"
    driver.save_screenshot(foto_path)
    try:
        with open(foto_path, "rb") as photo:
            requests.post(url_photo, data={"chat_id": CHAT_ID, "caption": mensagem}, files={"photo": photo})
        os.remove(foto_path)
    except:
        pass

def verificar_ingressos():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    driver = uc.Chrome(options=options, version_main=144)
    wait = WebDriverWait(driver, 30)

    print("Monitorando via Hierarquia H5 -> Div Inactive...")

    try:
        while True:
            for url in URLS:
                dia = "20" if "21-02" not in url else "21"
                print(f"\n--- Analisando Dia {dia} ---")
                
                try:
                    driver.get(url)
                    
                    # Navegação para a tela de ingressos
                    btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Ingressos')] | //button[contains(text(), 'Ingressos')]")))
                    driver.execute_script("arguments[0].click();", btn)
                    
                    # Seleção do Setor (Cadeira Superior)
                    time.sleep(10)
                    setor = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Cadeira Superior')]")))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", setor)
                    driver.execute_script("arguments[0].click();", setor)
                    
                    # Análise da Estrutura informada
                    time.sleep(6)
                    
                    try:
                        # Buscamos o h5 que contém EXATAMENTE 'Meia-Entrada'
                        # E subimos para a div que você descreveu (item-rate)
                        xpath_linha = "//h5[normalize-space()='Meia-Entrada']/ancestor::div[contains(@class, 'item-rate')][1]"
                        container_meia = driver.find_element(By.XPATH, xpath_linha)
                        
                        classes_da_div = container_meia.get_attribute("class")
                        texto_interno = container_meia.text.upper()

                        print(f"Linha localizada. Classes: {classes_da_div}")

                        # VERIFICAÇÃO TRIPLA DE DISPONIBILIDADE:
                        # A div NÃO pode ter a classe 'item-inactive'
                        # O texto 'ESGOTADO' não pode estar no span interno
                        # Não pode ser a linha de PCD (filtro extra)
                        is_inactive = "item-inactive" in classes_da_div
                        is_esgotado = "ESGOTADO" in texto_interno
                        is_pcd = "PCD" in texto_interno

                        if not is_inactive and not is_esgotado and not is_pcd:
                            print(f"Meia comum ativa detectada!")
                            enviar_telegram(f"INGRESSO DISPONÍVEL! Dia {dia}\n{url}", driver)
                            tocar_melodia_agradavel()
                        else:
                            status = "Inativa" if is_inactive else "Esgotada"
                            if is_pcd: status = "PCD (Ignorado)"
                            print(f"Dia {dia}: Meia localizada, mas está {status}.")

                    except Exception as e:
                        print(f"Não encontrei o h5 'Meia-Entrada' ou a div pai no Dia {dia}.")

                except Exception as e:
                    print(f"Falha no carregamento dos elementos: {e}")
                
                time.sleep(12)

            # Pausa aleatória entre ciclos
            time.sleep(random.randint(300, 450))

    finally:
        driver.quit()

if __name__ == "__main__":
    verificar_ingressos()