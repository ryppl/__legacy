import pygments.lexer
from pygments.lexer import RegexLexer, bygroups, using
from pygments.token import *

urls = (r'(?:git|http)(?:@|://)[^\s]+\.git', Operator.Word);

class GitCmdLineLexer(RegexLexer):
    aliases = ['git_cmdline']

    filenames = []

    kwds = r'(?:log|submodule|summary|reset|config|clone|status|remote|add|push|branch|pull|checkout|merge|rebase|diff|commit|fetch|symbolic-ref|svn|init|format-patch)\s';

    tokens = {
        'root' : [
         (r'<--[^\n]+', Generic.Prompt),
         (kwds, Generic.Deleted),
         urls,
         (r'\'[^\']+\'', Literal.String), # current branch
         (r'\*\s\w+\n', Name.Label), # current branch
         (r'-\w+ ', Operator),
         (r'/[\w\./]+', Name.Variable),
         (r'git', Text),
         (r'% git', Keyword),
         (r'$ git', Keyword),
         (r'"[^"]+"', Literal.String.Double),
         (r"'[^']+'", Literal.String.Single),
         (r'\*', Operator),
         (r'\s', Generic.Whitespace),
         (r'[^\s]+', Text),
         (r'(/\w+)+', Generic.Constant),
         ]
    }


class GitLexer(RegexLexer):
    name = "GitLexer"
    aliases = ['git_shell']

    filenames = []

    tokens = {
        'root' : [
        (r'% git.*\n', using(GitCmdLineLexer)),
        urls,
        (r'#[^\n]*\n', Comment),
        (r'([+-]?)([a-f0-9]{40}|[a-f0-9]{7}\.+[a-f0-9]{7})',
         bygroups(Generic.Output, Literal.Number.Hex)),
        (r'<--[^\n]+\n', Generic.Prompt),
        (r'^(% )(.*)(<--[^\n]+)', bygroups(Keyword, Text, Generic.Prompt)),
        (r'"[^"]+"', Literal.String.Double),
        (r"'[^']+'", Literal.String.Single),
        (r'[^\n\s]+', Generic.Output),
        (r'[\n\s]+', Generic.Whitespace),
        ]
    }

gitlexer = GitLexer()

def setup(app):
    app.add_lexer('git_shell', gitlexer)

