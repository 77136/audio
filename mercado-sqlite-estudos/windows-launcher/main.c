/*
 * Mercado SQL: abre o guia local no navegador padrao de HTTPS.
 * Nao instala componentes, nao modifica associacoes e nao executa SQL.
 * Todo o acesso a caminhos usa as APIs Unicode do Windows.
 */
#define UNICODE
#define _UNICODE
#define WIN32_LEAN_AND_MEAN
#ifndef _WIN32_WINNT
#define _WIN32_WINNT 0x0A00
#endif

#include <windows.h>
#include <shellapi.h>
#include <shlwapi.h>
#include <objbase.h>
#include <wchar.h>

#define MAX_PATH_CHARS 32768u
#define MAX_PARAMETER_CHARS 32760u

static WCHAR *allocate_chars(SIZE_T count)
{
    return (WCHAR *)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY,
                             count * sizeof(WCHAR));
}

static void release_text(WCHAR *text)
{
    if (text != NULL) {
        HeapFree(GetProcessHeap(), 0, text);
    }
}

static WCHAR *join_text(const WCHAR *left, const WCHAR *right)
{
    SIZE_T left_length = wcslen(left);
    SIZE_T right_length = wcslen(right);
    WCHAR *result = allocate_chars(left_length + right_length + 1);
    if (result != NULL) {
        CopyMemory(result, left, left_length * sizeof(WCHAR));
        CopyMemory(result + left_length, right,
                   (right_length + 1) * sizeof(WCHAR));
    }
    return result;
}

/* Nao depende do diretorio atual nem do nome dado ao executavel. */
static WCHAR *executable_directory(void)
{
    DWORD capacity = 256;
    for (;;) {
        WCHAR *path = allocate_chars(capacity);
        DWORD length;
        if (path == NULL) {
            return NULL;
        }
        length = GetModuleFileNameW(NULL, path, capacity);
        if (length == 0) {
            release_text(path);
            return NULL;
        }
        if (length < capacity) {
            while (length > 0 && path[length - 1] != L'\\'
                   && path[length - 1] != L'/') {
                --length;
            }
            if (length == 0) {
                release_text(path);
                return NULL;
            }
            path[length] = L'\0';
            return path;
        }
        release_text(path);
        if (capacity == MAX_PATH_CHARS) {
            return NULL;
        }
        capacity = capacity > MAX_PATH_CHARS / 2
                       ? MAX_PATH_CHARS : capacity * 2;
    }
}

/* O prefixo estendido permite verificar arquivos alem do MAX_PATH comum. */
static WCHAR *extended_path(const WCHAR *path)
{
    if (wcsncmp(path, L"\\\\?\\", 4) == 0) {
        return join_text(L"", path);
    }
    if (wcsncmp(path, L"\\\\", 2) == 0) {
        return join_text(L"\\\\?\\UNC\\", path + 2);
    }
    return join_text(L"\\\\?\\", path);
}

static BOOL file_exists(const WCHAR *path)
{
    WCHAR *extended = extended_path(path);
    DWORD attributes;
    if (extended == NULL) {
        return FALSE;
    }
    attributes = GetFileAttributesW(extended);
    release_text(extended);
    return attributes != INVALID_FILE_ATTRIBUTES
           && (attributes & FILE_ATTRIBUTE_DIRECTORY) == 0;
}

/* UrlCreateFromPathW nao aceita o prefixo estendido \\?\ em sua entrada. */
static WCHAR *path_for_url(const WCHAR *path)
{
    if (StrCmpNIW(path, L"\\\\?\\UNC\\", 8) == 0) {
        return join_text(L"\\\\", path + 8);
    }
    if (wcsncmp(path, L"\\\\?\\", 4) == 0) {
        return join_text(L"", path + 4);
    }
    return join_text(L"", path);
}

static WCHAR *guide_url(const WCHAR *guide_path)
{
    WCHAR *normal_path = path_for_url(guide_path);
    WCHAR *url;
    WCHAR *with_fragment;
    DWORD capacity;
    HRESULT result;
    if (normal_path == NULL) {
        return NULL;
    }
    /* Reserva para os caracteres escapados, inclusive nomes com acentos. */
    capacity = (DWORD)(wcslen(normal_path) * 9 + 64);
    url = allocate_chars(capacity);
    if (url == NULL) {
        release_text(normal_path);
        return NULL;
    }
    result = UrlCreateFromPathW(normal_path, url, &capacity, 0);
    release_text(normal_path);
    if (FAILED(result)) {
        release_text(url);
        return NULL;
    }
    with_fragment = join_text(url, L"#exercicios");
    release_text(url);
    return with_fragment;
}

/* Consulta apenas a associacao existente: nunca a altera. */
static WCHAR *https_browser(void)
{
    DWORD capacity = 0;
    HRESULT result;
    WCHAR *browser;
    result = AssocQueryStringW(ASSOCF_IS_PROTOCOL, ASSOCSTR_EXECUTABLE,
                              L"https", L"open", NULL, &capacity);
    if ((FAILED(result) && result != E_POINTER)
        || capacity == 0 || capacity > MAX_PATH_CHARS) {
        return NULL;
    }
    browser = allocate_chars((SIZE_T)capacity + 1);
    if (browser == NULL) {
        return NULL;
    }
    result = AssocQueryStringW(ASSOCF_IS_PROTOCOL, ASSOCSTR_EXECUTABLE,
                              L"https", L"open", browser, &capacity);
    if (FAILED(result) || browser[0] == L'\0') {
        release_text(browser);
        return NULL;
    }
    return browser;
}

static WCHAR *quoted_url(const WCHAR *url)
{
    SIZE_T length = wcslen(url);
    WCHAR *quoted = allocate_chars(length + 3);
    if (quoted != NULL) {
        quoted[0] = L'"';
        CopyMemory(quoted + 1, url, length * sizeof(WCHAR));
        quoted[length + 1] = L'"';
        quoted[length + 2] = L'\0';
    }
    return quoted;
}

static void show_error(const WCHAR *message)
{
    MessageBoxW(NULL, message, L"Mercado SQL", MB_OK | MB_ICONERROR);
}

int WINAPI WinMain(HINSTANCE instance, HINSTANCE previous,
                   LPSTR command_line, int show_command)
{
    WCHAR *directory = NULL;
    WCHAR *guide = NULL;
    WCHAR *database = NULL;
    WCHAR *url = NULL;
    WCHAR *browser = NULL;
    WCHAR *parameters = NULL;
    INT_PTR launched;
    int exit_code = 1;
    HRESULT com_result;
    (void)instance;
    (void)previous;
    (void)command_line;
    (void)show_command;

    com_result = CoInitializeEx(NULL, COINIT_APARTMENTTHREADED
                                     | COINIT_DISABLE_OLE1DDE);
    directory = executable_directory();
    if (directory == NULL) {
        show_error(L"Não foi possível localizar a pasta do Mercado SQL.\n\n"
                   L"Extraia todo o ZIP e tente novamente.");
        goto cleanup;
    }
    guide = join_text(directory, L"conteudo\\LEIA-ME.html");
    database = join_text(directory, L"conteudo\\mercado.db");
    if (guide == NULL || database == NULL
        || !file_exists(guide) || !file_exists(database)) {
        show_error(L"Não encontrei o guia e o banco de estudos.\n\n"
                   L"Extraia todo o ZIP. Mantenha Mercado SQL.exe ao lado "
                   L"da pasta conteudo, com todos os arquivos.");
        goto cleanup;
    }
    url = guide_url(guide);
    if (url == NULL || wcslen(url) > MAX_PARAMETER_CHARS) {
        show_error(L"Não foi possível abrir o guia a partir desta pasta.\n\n"
                   L"Tente extrair todo o pacote em um caminho mais curto, "
                   L"como C:\\Mercado SQL.");
        goto cleanup;
    }
    browser = https_browser();
    if (browser == NULL) {
        show_error(L"Não foi possível identificar o navegador padrão.\n\n"
                   L"Abra o arquivo conteudo\\LEIA-ME.html usando o seu navegador.");
        goto cleanup;
    }
    parameters = quoted_url(url);
    if (parameters == NULL) {
        show_error(L"Não foi possível preparar a abertura do guia.\n\n"
                   L"Tente abrir o Mercado SQL novamente.");
        goto cleanup;
    }
    /* O executavel recebe uma URL entre aspas, sem interpretador de comandos. */
    launched = (INT_PTR)ShellExecuteW(NULL, L"open", browser,
                                      parameters, directory, SW_SHOWNORMAL);
    if (launched <= 32) {
        show_error(L"Não foi possível abrir o navegador padrão.\n\n"
                   L"Abra o arquivo conteudo\\LEIA-ME.html pelo seu navegador.");
        goto cleanup;
    }
    exit_code = 0;

cleanup:
    release_text(parameters);
    release_text(browser);
    release_text(url);
    release_text(database);
    release_text(guide);
    release_text(directory);
    if (SUCCEEDED(com_result)) {
        CoUninitialize();
    }
    return exit_code;
}
