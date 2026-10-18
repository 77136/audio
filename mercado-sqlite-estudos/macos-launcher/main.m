#import <AppKit/AppKit.h>
#include <stdio.h>
#include <string.h>

// O aplicativo leva o material consigo; pode ser movido para qualquer pasta.
int main(int argc, const char *argv[]) {
    @autoreleasepool {
        NSBundle *bundle = [NSBundle mainBundle];
        NSURL *guide = [bundle URLForResource:@"LEIA-ME" withExtension:@"html"];
        NSURL *database = [bundle URLForResource:@"mercado" withExtension:@"db"];
        BOOL checkOnly = argc == 2 && strcmp(argv[1], "--check") == 0;
        if (!guide || !database) {
            if (checkOnly) {
                fputs("Os arquivos do guia ou do banco nao foram encontrados.\n", stderr);
            } else {
                NSAlert *alert = [[NSAlert alloc] init];
                alert.messageText = @"Não foi possível abrir o Mercado SQL";
                alert.informativeText = @"Extraia novamente o aplicativo do arquivo ZIP e tente abrir.";
                [alert addButtonWithTitle:@"OK"];
                [alert runModal];
            }
            return 1;
        }
        NSURLComponents *components = [NSURLComponents componentsWithURL:guide resolvingAgainstBaseURL:NO];
        components.fragment = @"exercicios";
        if (checkOnly) {
            puts(components.URL.absoluteString.UTF8String);
            return 0;
        }
        // Usa o navegador padrao de HTTPS, mesmo quando .html esta associado a um editor.
        NSURL *browser = [[NSWorkspace sharedWorkspace]
            URLForApplicationToOpenURL:[NSURL URLWithString:@"https://sqliteonline.com/"]];
        BOOL opened = NO;
        if (browser) {
            NSTask *task = [[NSTask alloc] init];
            task.executableURL = [NSURL fileURLWithPath:@"/usr/bin/open"];
            task.arguments = @[@"-a", browser.path, components.URL.absoluteString];
            NSError *error = nil;
            if ([task launchAndReturnError:&error]) {
                [task waitUntilExit];
                opened = task.terminationStatus == 0;
            }
        }
        if (!opened) {
            NSAlert *alert = [[NSAlert alloc] init];
            alert.messageText = @"Abra o guia no seu navegador";
            alert.informativeText = @"Escolha um navegador padrão no Mac e abra o Mercado SQL novamente.";
            [alert addButtonWithTitle:@"OK"];
            [alert runModal];
            return 1;
        }
        return 0;
    }
}
