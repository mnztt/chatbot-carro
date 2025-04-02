const fs = require('fs');
const axios = require('axios');
const cheerio = require('cheerio');
const url = require('url');

const baseUrl = 'https://adelveiculos.com.br/veiculos/carros/';
const lastPageButtonSelector = '.tt-pagination li:last-child a';

async function getTotalPages() {
    try {
        const response = await axios.get(baseUrl);
        const $ = cheerio.load(response.data);

        const ultimoBotao = $(lastPageButtonSelector);

        if (ultimoBotao.length === 0) {
            console.error('Botão "Último" não encontrado.');
            return 0;
        }

        const ultimoBotaoHref = ultimoBotao.attr('href');
        const regex = /pagina=(\d+)/;
        const match = ultimoBotaoHref.match(regex);

        if (match && match[1]) {
            const totalPages = parseInt(match[1], 10);
            return totalPages;
        } else {
            console.error('Não foi possível extrair o número total de páginas.');
            return 0;
        }
    } catch (error) {
        console.error('Erro ao obter o número total de páginas:', error.message);
        return 0;
    }
}

async function scrapeAllPages() {
    const totalPages = await getTotalPages();

    if (totalPages === 0) {
        console.error('Não foi possível obter o número total de páginas. Abortando.');
        return;
    }

    console.log('Número total de páginas:', totalPages);

    const todosVeiculos = [];

    for (let pagina = 1; pagina <= totalPages; pagina++) {
        const urlPagina = new url.URL(baseUrl);
        urlPagina.searchParams.set('pagina', pagina);

        try {
            const response = await axios.get(urlPagina.toString());
            const $ = cheerio.load(response.data);

            const cardSelector = '.dmi-car-list';

            $(cardSelector).each(async (index, element) => {
                const linkVeiculo = $(element).find('.tt-img').attr('href');
                const veiculoPath = linkVeiculo.replace(baseUrl, '');
                const linkCompleto = new url.URL(veiculoPath, baseUrl).toString();

                const veiculo = {
                    imagem: $(element).find('.tt-image-box').css('background-image'),
                    titulo: $(element).find('.tt-title a').text().trim(),
                    descricao: $(element).find('.tt-description').text().trim(),
                    anoModelo: $(element).find('.tt-year').text().trim(),
                    preco: $(element).find('.tt-price').text().trim(),
                    quilometragem: $(element).find('.tt-km').text().trim(),
                    detalhes: await scrapeDetails(linkCompleto)
                };

                todosVeiculos.push(veiculo);
            });

            console.log(`Página ${pagina} de ${totalPages} concluída.`);

        } catch (error) {
            console.error(`Erro durante o web scraping da página ${pagina}:`, error.message);
        }
    }

    const todosVeiculosJSON = JSON.stringify(todosVeiculos, null, 2);
    fs.writeFileSync('veiculos_all.json', todosVeiculosJSON);

    console.log('Dados de todos os veículos foram salvos em veiculos_all.json.');
}

async function scrapeDetails(linkCompleto) {
    try {
        console.log(`Obtendo detalhes do veículo: ${linkCompleto}`);

        const response = await axios.get(linkCompleto);
        const $ = cheerio.load(response.data);

        const detalhes = {};

        // Extrai as informações de detalhes do veículo
        const fichaBoxItems = $('.col-4 .ficha-box');
        if (fichaBoxItems.length === 0) {
            throw new Error('Detalhes do veículo não encontrados. Verifique o seletor.');
        }

        fichaBoxItems.each((index, element) => {
            const title = $(element).find('.tt-title').text().trim();
            const description = $(element).find('.tt-description').text().trim();
            detalhes[title.toLowerCase()] = description;
        });

        // Extrai os opcionais do veículo
        const opcionais = [];
        const opcionaisList = $('.dmi-opcionais.collapsible ul li');
        if (opcionaisList.length > 0) {
            opcionaisList.each((index, element) => {
                opcionais.push($(element).text().trim());
            });
        }

        detalhes.opcionais = opcionais;

        console.log('Detalhes obtidos com sucesso:', detalhes);

        return detalhes;
    } catch (error) {
        console.error(`Erro ao obter detalhes do veículo (${linkCompleto}):`, error.message);
        return {};
    }
}

scrapeAllPages();
