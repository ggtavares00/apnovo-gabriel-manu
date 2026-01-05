// Script para o formulário de confirmação de presença

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('rsvpForm');
    const nomeInput = document.getElementById('nome');
    const submitBtn = document.getElementById('submitBtn');
    const messageContainer = document.getElementById('messageContainer');

    // Event listener para o formulário
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const nome = nomeInput.value.trim();

        // Validação básica
        if (nome.length < 3) {
            showMessage('Por favor, digite seu nome completo (mínimo 3 caracteres).', 'error');
            return;
        }

        // Desabilitar botão durante o envio
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Confirmando...';

        try {
            const response = await fetch('/confirmar-presenca', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ nome: nome })
            });

            const data = await response.json();

            if (response.ok) {
                // Sucesso
                showMessage(
                    `✓ Presença confirmada com sucesso! Obrigado, ${nome}! 🎉`,
                    'success'
                );
                
                // Limpar formulário
                form.reset();
                
                // Scroll suave para a mensagem
                messageContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

            } else {
                // Erro da API
                showMessage(
                    data.detail || 'Erro ao confirmar presença. Tente novamente.',
                    'error'
                );
            }

        } catch (error) {
            // Erro de rede ou outro
            showMessage(
                'Erro de conexão. Verifique sua internet e tente novamente.',
                'error'
            );
            console.error('Erro:', error);

        } finally {
            // Reabilitar botão
            submitBtn.disabled = false;
            submitBtn.textContent = '✓ Confirmar Presença';
        }
    });

    // Função para exibir mensagens
    function showMessage(text, type) {
        messageContainer.innerHTML = `
            <div class="message ${type}">
                ${text}
            </div>
        `;

        // Remover mensagem após 5 segundos para mensagens de sucesso
        if (type === 'success') {
            setTimeout(() => {
                const message = messageContainer.querySelector('.message');
                if (message) {
                    message.style.opacity = '0';
                    setTimeout(() => {
                        messageContainer.innerHTML = '';
                    }, 300);
                }
            }, 5000);
        }
    }

    // Validação em tempo real
    nomeInput.addEventListener('input', function() {
        // Remove mensagens de erro ao digitar
        const errorMessage = messageContainer.querySelector('.message.error');
        if (errorMessage) {
            messageContainer.innerHTML = '';
        }
    });

    // Adicionar feedback visual ao focar no input
    nomeInput.addEventListener('focus', function() {
        this.parentElement.style.transform = 'scale(1.02)';
        this.parentElement.style.transition = 'transform 0.2s ease';
    });

    nomeInput.addEventListener('blur', function() {
        this.parentElement.style.transform = 'scale(1)';
    });
});
